"""Calendar service — fetches economic events or returns mock data."""

from __future__ import annotations

from typing import Any

from app.config import settings
from app.services.mock_data import get_mock_calendar


async def fetch_calendar(today_only: bool = False) -> list[dict[str, Any]]:
    """Return economic calendar events."""
    if settings.USE_MOCK_DATA:
        return get_mock_calendar(today_only=today_only)
    # Live FRED integration placeholder
    return get_mock_calendar(today_only=today_only)
