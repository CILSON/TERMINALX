"""Pydantic v2 schemas for economic calendar events."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EconomicEventResponse(BaseModel):
    id: UUID
    event_name: str
    country: str
    event_date: datetime
    forecast: str = ""
    actual: str = ""
    previous: str = ""
    impact: str = "medium"
    created_at: datetime

    model_config = {"from_attributes": True}


class CalendarListResponse(BaseModel):
    items: list[EconomicEventResponse]
    count: int
