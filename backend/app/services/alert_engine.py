"""Alert engine — checks price alerts against current quotes."""

from __future__ import annotations

from typing import Any
from datetime import datetime, timezone


def check_alerts(
    alerts: list[dict[str, Any]],
    quotes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Check which alerts are triggered by current quotes.

    Returns a list of triggered alert dicts with trigger details.
    """
    quote_map = {q["symbol"]: q for q in quotes}
    triggered = []

    for alert in alerts:
        if alert.get("triggered"):
            continue

        sym = alert.get("symbol", "").upper()
        q = quote_map.get(sym)
        if not q:
            continue

        price = q["price"]
        target = float(alert.get("target_value", 0))
        alert_type = alert.get("alert_type", "")

        fire = False
        if alert_type == "price_above" and price >= target:
            fire = True
        elif alert_type == "price_below" and price <= target:
            fire = True
        elif alert_type == "pct_change":
            pct = abs(q.get("change_pct", 0))
            if pct >= target:
                fire = True

        if fire:
            triggered.append({
                **alert,
                "triggered": True,
                "triggered_at": datetime.now(timezone.utc).isoformat(),
                "current_price": price,
                "message": f"Alert: {sym} {alert_type} {target} (current: {price})",
            })

    return triggered
