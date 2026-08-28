import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_membership, require_role
from app.core.database import get_db
from app.models.organization import Membership, Role
from app.models.quote import QuoteStatus
from app.schemas.invoice import InvoiceOut
from app.schemas.quote import QuoteCreate, QuoteDetailOut, QuoteOut, QuoteTransition, QuoteUpdate
from app.services import invoice_service, quote_service
from app.services.quote_service import (
    ClientNotInOrganizationError,
    InvalidTransitionError,
    ProjectNotInOrganizationError,
    QuoteLockedError,
    QuoteNotFoundError,
)

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("", response_model=list[QuoteOut])
def list_quotes(
    status_filter: QuoteStatus | None = None,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return quote_service.list_quotes(db, membership.organization_id, status_filter)


@router.post("", response_model=QuoteOut, status_code=status.HTTP_201_CREATED)
def create_quote(
    payload: QuoteCreate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return quote_service.create_quote(db, membership.organization_id, payload)
    except ClientNotInOrganizationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client introuvable")
    except ProjectNotInOrganizationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Projet introuvable")


@router.get("/{quote_id}", response_model=QuoteDetailOut)
def get_quote(
    quote_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return quote_service.get_quote(db, membership.organization_id, quote_id)
    except QuoteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis introuvable")


@router.patch("/{quote_id}", response_model=QuoteDetailOut)
def update_quote(
    quote_id: uuid.UUID,
    payload: QuoteUpdate,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return quote_service.update_quote(db, membership.organization_id, quote_id, payload)
    except QuoteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis introuvable")
    except QuoteLockedError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce devis n'est plus modifiable")
    except ProjectNotInOrganizationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Projet introuvable")


@router.post("/{quote_id}/transition", response_model=QuoteOut)
def transition_quote(
    quote_id: uuid.UUID,
    payload: QuoteTransition,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        return quote_service.transition_quote(db, membership.organization_id, quote_id, payload.status)
    except QuoteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis introuvable")
    except InvalidTransitionError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transition de statut invalide")


@router.post("/{quote_id}/convert-to-invoice", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED)
def convert_quote_to_invoice(
    quote_id: uuid.UUID,
    membership: Membership = Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    try:
        quote = quote_service.get_quote(db, membership.organization_id, quote_id)
    except QuoteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis introuvable")
    if quote.status != QuoteStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Seul un devis accepté peut être transformé en facture"
        )
    return invoice_service.create_invoice_from_quote(db, membership.organization_id, quote)


@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: uuid.UUID,
    membership: Membership = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    try:
        quote_service.delete_quote(db, membership.organization_id, quote_id)
    except QuoteNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis introuvable")
    except QuoteLockedError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce devis n'est plus modifiable")
    return None
