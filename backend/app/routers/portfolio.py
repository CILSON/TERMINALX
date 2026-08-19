"""Portfolio API router."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

# In-memory store for Phase 1 (no auth, single user)
_portfolios: list[dict] = [
    {
        "id": "default",
        "name": "Default",
        "holdings": [
            {"symbol": "NIFTY", "quantity": 1, "avg_price": 24200.00},
            {"symbol": "GOLD", "quantity": 10, "avg_price": 2280.00},
            {"symbol": "BTC", "quantity": 0.5, "avg_price": 62000.00},
            {"symbol": "USDINR", "quantity": 10000, "avg_price": 83.20},
        ],
    }
]


class HoldingCreate(BaseModel):
    symbol: str
    quantity: float
    avg_price: float


class PortfolioCreate(BaseModel):
    name: str = "Default"


@router.get("")
async def list_portfolios():
    """Return all portfolios with holdings."""
    return {"portfolios": _portfolios}


@router.post("")
async def create_portfolio(data: PortfolioCreate):
    """Create a new portfolio."""
    import uuid
    portfolio = {
        "id": str(uuid.uuid4()),
        "name": data.name,
        "holdings": [],
    }
    _portfolios.append(portfolio)
    return portfolio


@router.post("/{portfolio_id}/holdings")
async def add_holding(portfolio_id: str, data: HoldingCreate):
    """Add a holding to a portfolio."""
    for p in _portfolios:
        if p["id"] == portfolio_id:
            holding = {
                "symbol": data.symbol.upper(),
                "quantity": data.quantity,
                "avg_price": data.avg_price,
            }
            p["holdings"].append(holding)
            return {"portfolio": p}
    return {"error": "Portfolio not found"}, 404
