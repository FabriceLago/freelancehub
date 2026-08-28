import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, str_enum


class TokenPurpose(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class VerificationToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Jeton à usage unique pour la vérification d'email et la réinitialisation
    de mot de passe. On stocke un hash du jeton (jamais le jeton en clair) —
    comme un mot de passe, il ne doit pas être récupérable en cas de fuite DB."""

    __tablename__ = "verification_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    purpose: Mapped[TokenPurpose] = mapped_column(str_enum(TokenPurpose, 30), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
