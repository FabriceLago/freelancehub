import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crm import Prospect, ProspectStatus


def list_for_organization(
    db: Session, organization_id: uuid.UUID, status: ProspectStatus | None = None
) -> list[Prospect]:
    stmt = select(Prospect).where(Prospect.organization_id == organization_id)
    if status is not None:
        stmt = stmt.where(Prospect.status == status)
    stmt = stmt.order_by(Prospect.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_for_organization(db: Session, organization_id: uuid.UUID, prospect_id: uuid.UUID) -> Prospect | None:
    # Le filtre organization_id ICI, pas seulement côté service, est ce qui
    # empêche un membre d'une organisation de lire/modifier le prospect d'une
    # autre organisation en devinant un UUID — c'est la frontière tenant.
    return db.execute(
        select(Prospect).where(Prospect.id == prospect_id, Prospect.organization_id == organization_id)
    ).scalar_one_or_none()
