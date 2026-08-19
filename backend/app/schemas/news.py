"""Pydantic v2 schemas for news articles."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AIAnalysis(BaseModel):
    what_happened: str = ""
    why_it_matters: str = ""
    affected_assets: list[str] = Field(default_factory=list)
    bullish_for: list[str] = Field(default_factory=list)
    bearish_for: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0, le=1)


class NewsResponse(BaseModel):
    id: UUID
    headline: str
    summary: str | None = None
    body: str | None = None
    source: str = ""
    source_url: str = ""
    publisher: str = ""
    published_at: datetime
    importance: int = 50
    sentiment: str = "neutral"
    category: str = "NEWS"
    entities: list[str] = Field(default_factory=list)
    ai_analysis: AIAnalysis | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NewsListResponse(BaseModel):
    items: list[NewsResponse]
    total: int
    limit: int
    offset: int


class NewsSearchParams(BaseModel):
    q: str = ""
    category: str | None = None
    sentiment: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
