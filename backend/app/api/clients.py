import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership
from app.core.database import get_db
from app.models.organization import Membership
from app.schemas.client import ClientOut
from app.services import client_service
from app.services.client_service import ClientNotFoundError

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientOut])
def list_clients(membership: Membership = Depends(get_current_membership), db: Session = Depends(get_db)):
    return client_service.list_clients(db, membership.organization_id)


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return client_service.get_client(db, membership.organization_id, client_id)
    except ClientNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")
