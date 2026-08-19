"""News article model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class News(Base):
    __tablename__ = "news"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=uuid.uuid4,
    )
    headline: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    publisher: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    importance: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    sentiment: Mapped[str] = mapped_column(String(16), nullable=False, default="neutral")
    category: Mapped[str] = mapped_column(String(32), nullable=False, default="NEWS", index=True)
    entities: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    ai_analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # GIN index for full-text search over headline + summary
    __table_args__ = (
        Index(
            "ix_news_fts",
            text("to_tsvector('english', coalesce(headline, '') || ' ' || coalesce(summary, ''))"),
            postgresql_using="gin",
        ),
        Index("ix_news_published_at", "published_at"),
        Index("ix_news_importance", "importance"),
    )

    def __repr__(self) -> str:
        return f"<News {self.headline[:40]}>"
