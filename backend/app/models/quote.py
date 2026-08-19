"""Market quote / price model."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Quote(Base):
    __tablename__ = "quotes"

    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    asset_class: Mapped[str] = mapped_column(String(32), nullable=False)  # index, commodity, forex, crypto
    exchange: Mapped[str] = mapped_column(String(32), nullable=False)     # NSE, MCX, FOREX, CRYPTO
    price: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, default=0)
    change: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, default=0)
    change_pct: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False, default=0)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    high: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, default=0)
    low: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, default=0)
    open: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, default=0)
    prev_close: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, default=0)
    day_high: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, default=0)
    day_low: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Quote {self.symbol} @ {self.price}>"
