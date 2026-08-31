import enum
import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin, str_enum


class ProspectStatus(str, enum.Enum):
    CONTACTED = "contacted"
    DISCUSSING = "discussing"
    CONVERTED = "converted"
    LOST = "lost"


class Prospect(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "prospects"
    # Remplace l'index simple sur organization_id : toutes les listes filtrent
    # par organisation ET trient par created_at desc (voir prospect_repository)
    # — un index composite sert les deux d'un coup, sans étape de tri séparée
    # (mesuré : Sort external merge sur disque à 50k lignes sans cet index).
    __table_args__ = (Index("ix_prospects_org_created", "organization_id", "created_at"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[ProspectStatus] = mapped_column(
        str_enum(ProspectStatus, 20), default=ProspectStatus.CONTACTED, nullable=False
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Client(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clients"
    __table_args__ = (Index("ix_clients_org_created", "organization_id", "created_at"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    # Garde une trace du prospect d'origine sans bloquer sa suppression éventuelle.
    converted_from_prospect_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("prospects.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    projects: Mapped[list["Project"]] = relationship(back_populates="client")
