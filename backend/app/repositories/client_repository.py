import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crm import Client

# Voir prospect_repository._MAX_RESULTS — même filet de sécurité en attendant
# une vraie pagination.
_MAX_RESULTS = 200


def list_for_organization(db: Session, organization_id: uuid.UUID) -> list[Client]:
    stmt = (
        select(Client)
        .where(Client.organization_id == organization_id)
        .order_by(Client.created_at.desc())
        .limit(_MAX_RESULTS)
    )
    return list(db.execute(stmt).scalars().all())


def get_for_organization(db: Session, organization_id: uuid.UUID, client_id: uuid.UUID) -> Client | None:
    return db.execute(
        select(Client).where(Client.id == client_id, Client.organization_id == organization_id)
    ).scalar_one_or_none()
