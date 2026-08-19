"""Quotes API router."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings
from app.services.market_data import fetch_all_quotes, fetch_quote
from app.services.news_fetcher import fetch_news, search_news
from app.services.ai_analyzer import analyze_asset
from app.services.mock_data import get_mock_asset_intelligence, MOCK_ASSETS

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.get("")
async def list_quotes():
    """Return all tracked quotes."""
    quotes = await fetch_all_quotes()
    return {"quotes": quotes, "count": len(quotes)}


@router.get("/{symbol}")
async def get_quote(symbol: str):
    """Return a single quote."""
    quote = await fetch_quote(symbol.upper())
    if not quote:
        return {"error": f"Symbol {symbol} not found"}, 404
    return quote


@router.get("/{symbol}/intelligence")
async def get_asset_intelligence(symbol: str):
    """Return enriched asset data with Gemini AI analysis.

    Uses real price data + real news headlines as context for Gemini.
    Falls back to data-driven summary if Gemini unavailable.
    """
    sym = symbol.upper()

    if settings.USE_MOCK_DATA:
        return get_mock_asset_intelligence(sym)

    # ── Fetch real data ──
    quote = await fetch_quote(sym)
    info = MOCK_ASSETS.get(sym, {})
    name = info.get("name", sym)

    # Search news for this asset
    search_terms = {
        "NIFTY": "NIFTY 50", "BANKNIFTY": "Bank NIFTY", "SENSEX": "SENSEX",
        "GOLD": "gold price", "SILVER": "silver price",
        "BRENT": "brent crude oil", "WTI": "WTI crude oil",
        "USDINR": "rupee dollar", "DXY": "dollar index",
        "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "BNB": "BNB crypto",
    }
    query = search_terms.get(sym, name)
    related_news = await search_news(query, limit=5)

    if not related_news:
        all_news = await fetch_news(limit=50)
        sym_lower = sym.lower()
        name_lower = name.lower()
        related_news = [
            a for a in all_news
            if sym_lower in a.get("headline", "").lower()
            or name_lower in a.get("headline", "").lower()
        ][:5]

    # Sentiment from news
    sentiment_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
    for a in related_news:
        s = a.get("sentiment", "neutral")
        sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
    dominant = max(sentiment_counts, key=sentiment_counts.get)  # type: ignore

    # ── Gemini AI analysis ──
    headlines = [a["headline"] for a in related_news]
    price = quote.get("price", 0) if quote else 0
    change_pct = quote.get("change_pct", 0) if quote else 0
    day_high = quote.get("day_high", price) if quote else 0
    day_low = quote.get("day_low", price) if quote else 0

    ai_result = await analyze_asset(
        symbol=sym,
        name=name,
        price=price,
        change_pct=change_pct,
        day_high=day_high,
        day_low=day_low,
        news_headlines=headlines,
    )

    return {
        "symbol": sym,
        "quote": quote,
        "related_news": related_news,
        "earnings": {},
        "ai_summary": ai_result.get("summary", ""),
        "ai_outlook": ai_result.get("outlook", dominant),
        "ai_key_levels": ai_result.get("key_levels", {}),
        "ai_risk_factors": ai_result.get("risk_factors", []),
        "ai_catalysts": ai_result.get("catalysts", []),
        "sentiment": dominant,
        "sentiment_breakdown": sentiment_counts,
    }
