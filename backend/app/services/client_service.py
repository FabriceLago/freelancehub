import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.crm import Client
from app.repositories import client_repository
from app.schemas.client import ClientCreate, ClientUpdate


class ClientNotFoundError(AppError):
    pass


class ClientHasProjectsError(AppError):
    pass


def list_clients(db: Session, organization_id: uuid.UUID) -> list[Client]:
    return client_repository.list_for_organization(db, organization_id)


def get_client(db: Session, organization_id: uuid.UUID, client_id: uuid.UUID) -> Client:
    client = client_repository.get_for_organization(db, organization_id, client_id)
    if client is None:
        raise ClientNotFoundError()
    return client


def create_client(db: Session, organization_id: uuid.UUID, data: ClientCreate) -> Client:
    # converted_from_prospect_id reste None ici : seul prospect_service.convert_to_client
    # (Étape 8) a le droit de le renseigner, jamais une création directe.
    client = Client(organization_id=organization_id, **data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update_client(db: Session, organization_id: uuid.UUID, client_id: uuid.UUID, data: ClientUpdate) -> Client:
    client = get_client(db, organization_id, client_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, organization_id: uuid.UUID, client_id: uuid.UUID) -> None:
    client = get_client(db, organization_id, client_id)
    db.delete(client)
    try:
        db.commit()
    except IntegrityError:
        # projects.client_id est ON DELETE RESTRICT (Étape 3) : protège les
        # projets/devis/factures existants d'une suppression silencieuse.
        # On traduit la violation de contrainte en erreur métier lisible
        # plutôt que de laisser fuiter un 500 avec la trace SQL brute.
        db.rollback()
        raise ClientHasProjectsError()
