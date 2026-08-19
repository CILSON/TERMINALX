"""Pydantic v2 schemas for the Bloomberg-style command bar."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    command: str
    target: str = ""
    params: dict[str, Any] = Field(default_factory=dict)


class CommandResponse(BaseModel):
    type: str  # news, quote, calendar, intelligence, error, flow, earnings
    data: Any = None
    message: str = ""
