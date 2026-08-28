import enum
import uuid
from datetime import date, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, str_enum


class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class Quote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quotes"
    # Numérotation lisible (ex: "DEV-2026-014") unique par organisation, pas globalement.
    __table_args__ = (UniqueConstraint("organization_id", "number", name="uq_quote_number_per_org"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[QuoteStatus] = mapped_column(
        str_enum(QuoteStatus, 20), default=QuoteStatus.DRAFT, nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    # Montants en centimes (integer) : jamais de float sur de l'argent.
    subtotal_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)  # ex: 20.00 = 20%
    total_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    valid_until: Mapped[date | None] = mapped_column(nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    client: Mapped["Client"] = relationship()
    line_items: Mapped[list["QuoteLineItem"]] = relationship(back_populates="quote", cascade="all, delete-orphan")


class QuoteLineItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "quote_line_items"

    quote_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quotes.id", ondelete="CASCADE"), index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1, nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    quote: Mapped["Quote"] = relationship(back_populates="line_items")
