import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, require_role
from app.core.database import get_db
from app.models.crm import ProspectStatus
from app.models.organization import Membership, Role
from app.schemas.client import ClientOut
from app.schemas.prospect import ProspectCreate, ProspectOut, ProspectUpdate
from app.services import prospect_service
from app.services.prospect_service import CannotSetConvertedDirectlyError, ProspectNotFoundError

router = APIRouter(prefix="/prospects", tags=["prospects"])


@router.get("", response_model=list[ProspectOut])
def list_prospects(
    status_filter: ProspectStatus | None = None,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return prospect_service.list_prospects(db, membership.organization_id, status_filter)


@router.post("", response_model=ProspectOut, status_code=status.HTTP_201_CREATED)
def create_prospect(
    payload: ProspectCreate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return prospect_service.create_prospect(db, membership.organization_id, payload)


@router.get("/{prospect_id}", response_model=ProspectOut)
def get_prospect(
    prospect_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return prospect_service.get_prospect(db, membership.organization_id, prospect_id)
    except ProspectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect introuvable")


@router.patch("/{prospect_id}", response_model=ProspectOut)
def update_prospect(
    prospect_id: uuid.UUID,
    payload: ProspectUpdate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return prospect_service.update_prospect(db, membership.organization_id, prospect_id, payload)
    except ProspectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect introuvable")
    except CannotSetConvertedDirectlyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisez POST /prospects/{id}/convert pour convertir un prospect en client",
        )


@router.post("/{prospect_id}/convert", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def convert_prospect(
    prospect_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return prospect_service.convert_to_client(db, membership.organization_id, prospect_id)
    except ProspectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect introuvable")


@router.delete("/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prospect(
    prospect_id: uuid.UUID,
    membership: Membership = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    try:
        prospect_service.delete_prospect(db, membership.organization_id, prospect_id)
    except ProspectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect introuvable")
    return None
