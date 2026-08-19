"""Alerts API router."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# In-memory store for Phase 1
_alerts: list[dict] = []


class AlertCreate(BaseModel):
    symbol: str
    alert_type: str  # price_above, price_below, pct_change
    target_value: float


@router.get("")
async def list_alerts():
    """Return all alerts."""
    return {"alerts": _alerts, "count": len(_alerts)}


@router.post("")
async def create_alert(data: AlertCreate):
    """Create a new price alert."""
    alert = {
        "id": str(uuid.uuid4()),
        "symbol": data.symbol.upper(),
        "alert_type": data.alert_type,
        "target_value": data.target_value,
        "triggered": False,
        "triggered_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _alerts.append(alert)
    return alert


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """Delete an alert."""
    global _alerts
    _alerts = [a for a in _alerts if a["id"] != alert_id]
    return {"status": "deleted", "id": alert_id}
