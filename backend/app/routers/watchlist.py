"""Watchlist API router."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

# In-memory store for Phase 1
_watchlist: dict = {
    "id": "default",
    "name": "Default",
    "symbols": ["NIFTY", "BANKNIFTY", "GOLD", "BTC", "USDINR", "BRENT"],
}


class WatchlistUpdate(BaseModel):
    symbol: str


@router.get("")
async def get_watchlist():
    """Return the default watchlist."""
    return _watchlist


@router.post("")
async def add_to_watchlist(data: WatchlistUpdate):
    """Add a symbol to the watchlist."""
    sym = data.symbol.upper()
    if sym not in _watchlist["symbols"]:
        _watchlist["symbols"].append(sym)
    return _watchlist


@router.delete("/{symbol}")
async def remove_from_watchlist(symbol: str):
    """Remove a symbol from the watchlist."""
    sym = symbol.upper()
    if sym in _watchlist["symbols"]:
        _watchlist["symbols"].remove(sym)
    return _watchlist
