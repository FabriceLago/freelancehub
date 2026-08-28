import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, str_enum


class PlanCode(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    BUSINESS = "business"


class SubscriptionStatus(str, enum.Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"


class Plan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Référentiel des plans (Free/Starter/Pro/Business) — données de
    configuration, pas de logique métier. Seedé en base, pas modifié par
    les utilisateurs. Voir Phase 10 (Stripe) pour stripe_price_id."""

    __tablename__ = "plans"

    code: Mapped[PlanCode] = mapped_column(str_enum(PlanCode, 20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    max_prospects: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = illimité
    max_documents_per_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_generations_per_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Subscription(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subscriptions"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, index=True
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id", ondelete="RESTRICT"))
    status: Mapped[SubscriptionStatus] = mapped_column(
        str_enum(SubscriptionStatus, 20), default=SubscriptionStatus.TRIALING
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="subscription")
    plan: Mapped["Plan"] = relationship()
