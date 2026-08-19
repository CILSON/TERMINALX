"""Pydantic v2 schemas for portfolios and holdings."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class HoldingCreate(BaseModel):
    symbol: str
    quantity: Decimal
    avg_price: Decimal


class HoldingResponse(BaseModel):
    id: UUID
    portfolio_id: UUID
    symbol: str
    quantity: Decimal
    avg_price: Decimal
    added_at: datetime

    model_config = {"from_attributes": True}


class PortfolioCreate(BaseModel):
    name: str = Field(default="Default", max_length=128)


class PortfolioResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    holdings: list[HoldingResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
