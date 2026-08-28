import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.crm import Client
from app.repositories import client_repository


class ClientNotFoundError(AppError):
    pass


def list_clients(db: Session, organization_id: uuid.UUID) -> list[Client]:
    return client_repository.list_for_organization(db, organization_id)


def get_client(db: Session, organization_id: uuid.UUID, client_id: uuid.UUID) -> Client:
    client = client_repository.get_for_organization(db, organization_id, client_id)
    if client is None:
        raise ClientNotFoundError()
    return client
