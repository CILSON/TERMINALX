"""ORM models package — import all models so Alembic can discover them."""

from app.models.base import Base
from app.models.alert import Alert
from app.models.calendar import EconomicEvent
from app.models.news import News
from app.models.portfolio import Portfolio, PortfolioHolding
from app.models.quote import Quote
from app.models.watchlist import Watchlist

__all__ = [
    "Base",
    "Alert",
    "EconomicEvent",
    "News",
    "Portfolio",
    "PortfolioHolding",
    "Quote",
    "Watchlist",
]
