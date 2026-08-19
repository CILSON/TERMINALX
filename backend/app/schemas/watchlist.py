"""Pydantic v2 schemas for watchlists."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WatchlistUpdate(BaseModel):
    symbol: str


class WatchlistResponse(BaseModel):
    id: UUID
    name: str
    symbols: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}
