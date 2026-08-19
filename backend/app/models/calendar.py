"""Economic calendar event model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EconomicEvent(Base):
    __tablename__ = "economic_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=uuid.uuid4,
    )
    event_name: Mapped[str] = mapped_column(String(256), nullable=False)
    country: Mapped[str] = mapped_column(String(8), nullable=False)  # IN, US, etc.
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    forecast: Mapped[str] = mapped_column(Text, nullable=False, default="")
    actual: Mapped[str] = mapped_column(Text, nullable=False, default="")
    previous: Mapped[str] = mapped_column(Text, nullable=False, default="")
    impact: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")  # high, medium, low
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<EconomicEvent {self.event_name}>"
