import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.crm import Client, Prospect, ProspectStatus
from app.repositories import prospect_repository
from app.schemas.prospect import ProspectCreate, ProspectUpdate


class ProspectNotFoundError(AppError):
    pass


class CannotSetConvertedDirectlyError(AppError):
    pass


def list_prospects(db: Session, organization_id: uuid.UUID, status: ProspectStatus | None) -> list[Prospect]:
    return prospect_repository.list_for_organization(db, organization_id, status)


def get_prospect(db: Session, organization_id: uuid.UUID, prospect_id: uuid.UUID) -> Prospect:
    prospect = prospect_repository.get_for_organization(db, organization_id, prospect_id)
    if prospect is None:
        raise ProspectNotFoundError()
    return prospect


def create_prospect(db: Session, organization_id: uuid.UUID, data: ProspectCreate) -> Prospect:
    prospect = Prospect(organization_id=organization_id, **data.model_dump())
    db.add(prospect)
    db.commit()
    db.refresh(prospect)
    return prospect


def update_prospect(
    db: Session, organization_id: uuid.UUID, prospect_id: uuid.UUID, data: ProspectUpdate
) -> Prospect:
    prospect = get_prospect(db, organization_id, prospect_id)
    updates = data.model_dump(exclude_unset=True)
    if updates.get("status") == ProspectStatus.CONVERTED:
        raise CannotSetConvertedDirectlyError()
    for field, value in updates.items():
        setattr(prospect, field, value)
    db.commit()
    db.refresh(prospect)
    return prospect


def delete_prospect(db: Session, organization_id: uuid.UUID, prospect_id: uuid.UUID) -> None:
    prospect = get_prospect(db, organization_id, prospect_id)
    db.delete(prospect)
    db.commit()


def convert_to_client(db: Session, organization_id: uuid.UUID, prospect_id: uuid.UUID) -> Client:
    """Crée le Client à partir du prospect et marque celui-ci CONVERTED — les
    deux dans la même transaction, jamais l'un sans l'autre (sinon on se
    retrouve avec un prospect "converti" sans client, ou l'inverse)."""
    prospect = get_prospect(db, organization_id, prospect_id)
    client = Client(
        organization_id=organization_id,
        converted_from_prospect_id=prospect.id,
        name=prospect.name,
        email=prospect.email,
        phone=prospect.phone,
    )
    prospect.status = ProspectStatus.CONVERTED
    db.add(client)
    db.commit()
    db.refresh(client)
    return client
