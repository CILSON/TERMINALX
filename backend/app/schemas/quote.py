"""Pydantic v2 schemas for market quotes."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class QuoteResponse(BaseModel):
    symbol: str
    name: str
    asset_class: str
    exchange: str
    price: Decimal
    change: Decimal
    change_pct: Decimal
    volume: int = 0
    high: Decimal = Decimal("0")
    low: Decimal = Decimal("0")
    open: Decimal = Decimal("0")
    prev_close: Decimal = Decimal("0")
    day_high: Decimal = Decimal("0")
    day_low: Decimal = Decimal("0")
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuoteListResponse(BaseModel):
    items: list[QuoteResponse]
    count: int
