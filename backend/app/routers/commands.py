"""Bloomberg-style command engine router."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.market_data import fetch_all_quotes, fetch_quote
from app.services.news_fetcher import fetch_news, search_news
from app.services.calendar_service import fetch_calendar
from app.services.mock_data import (
    get_mock_asset_intelligence,
    get_mock_fii_dii_flow,
    get_mock_earnings_data,
    MOCK_ASSETS,
)

router = APIRouter(prefix="/api", tags=["commands"])

# Symbols that can be used as commands
ASSET_COMMANDS = set(MOCK_ASSETS.keys())


class CommandRequest(BaseModel):
    command: str
    target: str = ""
    params: dict = {}


@router.post("/command")
async def execute_command(req: CommandRequest):
    """Execute a Bloomberg-style terminal command."""
    cmd = req.command.strip().upper()
    target = req.target.strip().upper()

    # ── NEWS commands ──────────────────────────────────────
    if cmd == "NEWS":
        articles = await fetch_news(category=target or None, limit=30)
        return {"type": "news", "data": articles}

    if cmd == "TOP":
        articles = await fetch_news(category="TOP", limit=20)
        return {"type": "news", "data": articles}

    if cmd == "INDIA":
        articles = await fetch_news(category="INDIA", limit=20)
        return {"type": "news", "data": articles}

    if cmd == "GLOBAL":
        articles = await fetch_news(category="GLOBAL", limit=20)
        return {"type": "news", "data": articles}

    # ── Market commands ────────────────────────────────────
    if cmd == "MKT":
        quotes = await fetch_all_quotes()
        return {"type": "quote", "data": quotes}

    if cmd == "FX":
        quotes = await fetch_all_quotes()
        fx = [q for q in quotes if q.get("asset_class") == "forex"]
        return {"type": "quote", "data": fx}

    if cmd == "CMDTY":
        quotes = await fetch_all_quotes()
        cmdty = [q for q in quotes if q.get("asset_class") == "commodity"]
        return {"type": "quote", "data": cmdty}

    if cmd == "CRYPTO":
        articles = await fetch_news(category="CRYPTO", limit=20)
        return {"type": "news", "data": articles}

    # ── Calendar / Earnings ────────────────────────────────
    if cmd == "CAL":
        events = await fetch_calendar()
        return {"type": "calendar", "data": events}

    if cmd == "EARN":
        earnings = get_mock_earnings_data()
        return {"type": "earnings", "data": earnings}

    if cmd == "FLOW":
        flow = get_mock_fii_dii_flow()
        return {"type": "flow", "data": flow}

    # ── Search ─────────────────────────────────────────────
    if cmd == "SEARCH" and target:
        results = await search_news(target)
        return {"type": "search", "data": results}

    # ── Asset-specific commands (NIFTY, GOLD, BTC, etc.) ──
    if cmd in ASSET_COMMANDS:
        intel = get_mock_asset_intelligence(cmd)
        return {"type": "asset", "data": intel}

    # ── Unknown ────────────────────────────────────────────
    return {
        "type": "error",
        "message": f"Unknown command: {cmd}",
        "available": sorted(
            ["NEWS", "TOP", "MKT", "INDIA", "GLOBAL", "FX", "CMDTY",
             "CRYPTO", "CAL", "EARN", "FLOW", "SEARCH"] + sorted(ASSET_COMMANDS)
        ),
    }
