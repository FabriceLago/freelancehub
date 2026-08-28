import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, require_role
from app.core.database import get_db
from app.models.invoice import InvoiceStatus
from app.models.organization import Membership, Role
from app.schemas.invoice import InvoiceCreate, InvoiceDetailOut, InvoiceOut, InvoiceTransition, InvoiceUpdate
from app.services import invoice_service
from app.services.invoice_service import (
    AlreadyPaidError,
    ClientNotInOrganizationError,
    InvalidTransitionError,
    InvoiceLockedError,
    InvoiceNotFoundError,
    ProjectNotInOrganizationError,
)

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=list[InvoiceOut])
def list_invoices(
    status_filter: InvoiceStatus | None = None,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return invoice_service.list_invoices(db, membership.organization_id, status_filter)


@router.post("", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return invoice_service.create_invoice(db, membership.organization_id, payload)
    except ClientNotInOrganizationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client introuvable")
    except ProjectNotInOrganizationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Projet introuvable")


@router.get("/{invoice_id}", response_model=InvoiceDetailOut)
def get_invoice(
    invoice_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return invoice_service.get_invoice(db, membership.organization_id, invoice_id)
    except InvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facture introuvable")


@router.patch("/{invoice_id}", response_model=InvoiceDetailOut)
def update_invoice(
    invoice_id: uuid.UUID,
    payload: InvoiceUpdate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return invoice_service.update_invoice(db, membership.organization_id, invoice_id, payload)
    except InvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facture introuvable")
    except InvoiceLockedError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette facture n'est plus modifiable")
    except ProjectNotInOrganizationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Projet introuvable")


@router.post("/{invoice_id}/transition", response_model=InvoiceOut)
def transition_invoice(
    invoice_id: uuid.UUID,
    payload: InvoiceTransition,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return invoice_service.transition_invoice(db, membership.organization_id, invoice_id, payload.status)
    except InvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facture introuvable")
    except InvalidTransitionError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transition de statut invalide")


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceOut)
def mark_invoice_paid(
    invoice_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return invoice_service.mark_paid(db, membership.organization_id, invoice_id)
    except InvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facture introuvable")
    except AlreadyPaidError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette facture est déjà payée")


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: uuid.UUID,
    membership: Membership = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    try:
        invoice_service.delete_invoice(db, membership.organization_id, invoice_id)
    except InvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facture introuvable")
    except InvoiceLockedError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cette facture n'est plus modifiable")
    return None
