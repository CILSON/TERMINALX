"""Pydantic v2 schemas for price alerts."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AlertCreate(BaseModel):
    symbol: str
    alert_type: str  # price_above, price_below, pct_change
    target_value: Decimal


class AlertResponse(BaseModel):
    id: UUID
    symbol: str
    alert_type: str
    target_value: Decimal
    triggered: bool = False
    triggered_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
