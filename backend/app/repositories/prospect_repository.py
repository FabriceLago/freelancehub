import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crm import Prospect, ProspectStatus

# Filet de sécurité tant qu'il n'y a pas de pagination côté frontend (Phase 20) :
# sans lui, une organisation avec des dizaines de milliers de prospects
# renverrait tout d'un coup. 200 couvre largement un usage normal en attendant
# une vraie pagination (offset/curseur + "charger plus" côté UI).
_MAX_RESULTS = 200


def list_for_organization(
    db: Session, organization_id: uuid.UUID, status: ProspectStatus | None = None
) -> list[Prospect]:
    stmt = select(Prospect).where(Prospect.organization_id == organization_id)
    if status is not None:
        stmt = stmt.where(Prospect.status == status)
    stmt = stmt.order_by(Prospect.created_at.desc()).limit(_MAX_RESULTS)
    return list(db.execute(stmt).scalars().all())


def get_for_organization(db: Session, organization_id: uuid.UUID, prospect_id: uuid.UUID) -> Prospect | None:
    # Le filtre organization_id ICI, pas seulement côté service, est ce qui
    # empêche un membre d'une organisation de lire/modifier le prospect d'une
    # autre organisation en devinant un UUID — c'est la frontière tenant.
    return db.execute(
        select(Prospect).where(Prospect.id == prospect_id, Prospect.organization_id == organization_id)
    ).scalar_one_or_none()
