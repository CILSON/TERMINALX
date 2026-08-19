"""Market data service — fetches live quotes from Yahoo Finance or mock data.

Uses yfinance in a thread executor so the async event loop is never blocked.
Falls back to mock data on any error.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.services.mock_data import get_mock_quotes, simulate_quote_update, MOCK_ASSETS

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Yahoo Finance ticker mapping
# ──────────────────────────────────────────────────────────────────────────────
YAHOO_SYMBOLS: dict[str, str] = {
    # Indian Indices
    "NIFTY":     "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY":  "NIFTY_FIN_SERVICE.NS",
    "MIDCAP":    "^NSEMDCP50",
    "SENSEX":    "^BSESN",
    # Commodities
    "GOLD":   "GC=F",
    "SILVER": "SI=F",
    "BRENT":  "BZ=F",
    "WTI":    "CL=F",
    "NATGAS": "NG=F",
    "COPPER": "HG=F",
    # Forex
    "USDINR": "USDINR=X",
    "EURINR": "EURINR=X",
    "GBPINR": "GBPINR=X",
    "DXY":    "DX-Y.NYB",
    "EURUSD": "EURUSD=X",
    # Crypto
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "BNB": "BNB-USD",
}

# Reverse mapping: Yahoo ticker → our symbol
_REVERSE_MAP = {v: k for k, v in YAHOO_SYMBOLS.items()}


def _yf_fetch_all() -> list[dict[str, Any]]:
    """Synchronous Yahoo Finance fetch — runs in thread executor."""
    import yfinance as yf

    quotes: list[dict[str, Any]] = []
    now_str = datetime.now(timezone.utc).isoformat()

    for our_symbol, yahoo_ticker in YAHOO_SYMBOLS.items():
        try:
            info = MOCK_ASSETS.get(our_symbol, {})
            ticker = yf.Ticker(yahoo_ticker)
            fi = ticker.fast_info

            price = float(fi.last_price)
            prev_close = float(fi.previous_close) if fi.previous_close else price
            change = round(price - prev_close, 4)
            change_pct = round((change / prev_close) * 100, 4) if prev_close else 0.0

            day_high = float(fi.day_high) if fi.day_high else price
            day_low = float(fi.day_low) if fi.day_low else price
            open_price = float(fi.open) if fi.open else price
            volume = int(fi.last_volume) if fi.last_volume else 0

            quotes.append({
                "symbol": our_symbol,
                "name": info.get("name", our_symbol),
                "asset_class": info.get("asset_class", "index"),
                "exchange": info.get("exchange", "NSE"),
                "price": round(price, 4),
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
                "high": round(day_high, 4),
                "low": round(day_low, 4),
                "open": round(open_price, 4),
                "prev_close": round(prev_close, 4),
                "day_high": round(day_high, 4),
                "day_low": round(day_low, 4),
                "updated_at": now_str,
            })
        except Exception as e:
            logger.error("Error fetching %s (%s): %s", our_symbol, yahoo_ticker, e)

    return quotes


def _yf_fetch_single(symbol: str) -> dict[str, Any] | None:
    """Synchronous single-ticker fetch."""
    import yfinance as yf

    yahoo_ticker = YAHOO_SYMBOLS.get(symbol.upper())
    if not yahoo_ticker:
        return None

    info = MOCK_ASSETS.get(symbol.upper(), {})
    try:
        ticker = yf.Ticker(yahoo_ticker)
        fast_info = ticker.fast_info

        price = float(fast_info.last_price)
        prev_close = float(fast_info.previous_close) if fast_info.previous_close else price
        change = round(price - prev_close, 4)
        change_pct = round((change / prev_close) * 100, 4) if prev_close else 0

        return {
            "symbol": symbol.upper(),
            "name": info.get("name", symbol),
            "asset_class": info.get("asset_class", "index"),
            "exchange": info.get("exchange", "NSE"),
            "price": round(price, 4),
            "change": change,
            "change_pct": change_pct,
            "volume": int(getattr(fast_info, "last_volume", 0) or 0),
            "high": round(float(getattr(fast_info, "day_high", price) or price), 4),
            "low": round(float(getattr(fast_info, "day_low", price) or price), 4),
            "open": round(float(getattr(fast_info, "open", price) or price), 4),
            "prev_close": round(prev_close, 4),
            "day_high": round(float(getattr(fast_info, "day_high", price) or price), 4),
            "day_low": round(float(getattr(fast_info, "day_low", price) or price), 4),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error("yfinance single fetch error for %s: %s", symbol, e)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Async public API
# ──────────────────────────────────────────────────────────────────────────────
async def fetch_all_quotes(redis_client=None) -> list[dict[str, Any]]:
    """Return current quotes for all tracked assets."""
    # Check Redis cache first
    if redis_client:
        try:
            cached = await redis_client.get("terminalx:quotes:all")
            if cached:
                return json.loads(cached)
        except Exception:
            pass

    if settings.USE_MOCK_DATA:
        quotes = get_mock_quotes()
    else:
        try:
            quotes = await asyncio.to_thread(_yf_fetch_all)
            if not quotes:
                logger.warning("Yahoo Finance returned empty, falling back to mock")
                quotes = get_mock_quotes()
        except Exception as e:
            logger.error("Live quotes failed: %s — falling back to mock", e)
            quotes = get_mock_quotes()

    # Cache
    if redis_client:
        try:
            await redis_client.set("terminalx:quotes:all", json.dumps(quotes), ex=30)
        except Exception:
            pass

    return quotes


async def fetch_quote(symbol: str, redis_client=None) -> dict[str, Any] | None:
    """Return a single quote for *symbol*."""
    sym = symbol.upper()

    if redis_client:
        try:
            cached = await redis_client.get(f"terminalx:quote:{sym}")
            if cached:
                return json.loads(cached)
        except Exception:
            pass

    if settings.USE_MOCK_DATA:
        if sym not in MOCK_ASSETS:
            return None
        quote = simulate_quote_update(sym)
    else:
        try:
            quote = await asyncio.to_thread(_yf_fetch_single, sym)
            if not quote:
                quote = simulate_quote_update(sym) if sym in MOCK_ASSETS else None
        except Exception as e:
            logger.error("Live single fetch failed for %s: %s", sym, e)
            quote = simulate_quote_update(sym) if sym in MOCK_ASSETS else None

    if redis_client and quote:
        try:
            await redis_client.set(f"terminalx:quote:{sym}", json.dumps(quote), ex=30)
        except Exception:
            pass

    return quote


async def update_all_quotes(redis_client=None) -> list[dict[str, Any]]:
    """Generate fresh ticks for all assets and cache them.

    In mock mode: generates random ticks.
    In live mode: fetches from Yahoo Finance.
    """
    if settings.USE_MOCK_DATA:
        quotes = []
        for sym in MOCK_ASSETS:
            q = simulate_quote_update(sym)
            quotes.append(q)
            if redis_client:
                try:
                    await redis_client.set(f"terminalx:quote:{sym}", json.dumps(q), ex=30)
                except Exception:
                    pass
    else:
        try:
            quotes = await asyncio.to_thread(_yf_fetch_all)
            if not quotes:
                logger.warning("Live update returned empty, using mock ticks")
                quotes = [simulate_quote_update(sym) for sym in MOCK_ASSETS]
        except Exception as e:
            logger.error("Live update failed: %s — using mock", e)
            quotes = [simulate_quote_update(sym) for sym in MOCK_ASSETS]

        # Cache individual quotes
        if redis_client:
            for q in quotes:
                try:
                    await redis_client.set(
                        f"terminalx:quote:{q['symbol']}", json.dumps(q), ex=30
                    )
                except Exception:
                    pass

    # Cache the full list
    if redis_client:
        try:
            await redis_client.set("terminalx:quotes:all", json.dumps(quotes), ex=30)
        except Exception:
            pass

    return quotes
