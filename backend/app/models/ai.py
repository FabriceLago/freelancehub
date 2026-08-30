import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AiGeneration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Une ligne par génération IA réussie — sert à la fois de journal
    d'usage (logging, coûts) et de compteur pour le quota mensuel par plan
    (Plan.ai_generations_per_month, voir Étape 4)."""

    __tablename__ = "ai_generations"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # "quote_draft", "reminder_draft"
