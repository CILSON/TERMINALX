"""Calendar API router."""

from __future__ import annotations

from fastapi import APIRouter

from app.services.calendar_service import fetch_calendar

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("")
async def list_calendar():
    """Return all economic calendar events."""
    events = await fetch_calendar()
    return {"events": events, "count": len(events)}


@router.get("/today")
async def today_calendar():
    """Return today's economic events."""
    events = await fetch_calendar(today_only=True)
    return {"events": events, "count": len(events)}
