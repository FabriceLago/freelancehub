import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Role(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Représente l'activité freelance d'un utilisateur. Créée automatiquement
    à l'inscription — c'est la frontière d'isolation multi-tenant (Phase 11)."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    subscription: Mapped["Subscription | None"] = relationship(
        back_populates="organization", cascade="all, delete-orphan", uselist=False
    )


class Membership(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Table de jointure user <-> organization, porteuse du rôle. Une requête
    qui touche aux données d'une organisation doit toujours vérifier qu'il
    existe une Membership pour l'utilisateur courant sur cette organisation."""

    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False, length=20), default=Role.OWNER, nullable=False)

    user: Mapped["User"] = relationship(back_populates="memberships")
    organization: Mapped["Organization"] = relationship(back_populates="memberships")
