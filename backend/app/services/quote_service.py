import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.quote import Quote, QuoteLineItem, QuoteStatus
from app.repositories import client_repository, project_repository, quote_repository
from app.schemas.quote import QuoteCreate, QuoteUpdate
from app.utils.money import compute_totals
from app.utils.numbering import generate_number


class QuoteNotFoundError(AppError):
    pass


class ClientNotInOrganizationError(AppError):
    pass


class ProjectNotInOrganizationError(AppError):
    pass


class QuoteLockedError(AppError):
    """Le devis n'est plus en DRAFT : montants et lignes ne peuvent plus changer."""


class InvalidTransitionError(AppError):
    pass


# DRAFT -> SENT -> {ACCEPTED, DECLINED, EXPIRED} : une fois accepté/refusé/
# expiré, un devis est un document figé, pas un statut qu'on peut continuer
# à faire évoluer (contrairement à Prospect où LOST n'est pas terminal).
_ALLOWED_TRANSITIONS: dict[QuoteStatus, set[QuoteStatus]] = {
    QuoteStatus.DRAFT: {QuoteStatus.SENT},
    QuoteStatus.SENT: {QuoteStatus.ACCEPTED, QuoteStatus.DECLINED, QuoteStatus.EXPIRED},
}


def list_quotes(db: Session, organization_id: uuid.UUID, status: QuoteStatus | None) -> list[Quote]:
    return quote_repository.list_for_organization(db, organization_id, status)


def get_quote(db: Session, organization_id: uuid.UUID, quote_id: uuid.UUID) -> Quote:
    quote = quote_repository.get_for_organization(db, organization_id, quote_id)
    if quote is None:
        raise QuoteNotFoundError()
    return quote


def _validate_client_and_project(db: Session, organization_id: uuid.UUID, client_id: uuid.UUID, project_id) -> None:
    if client_repository.get_for_organization(db, organization_id, client_id) is None:
        raise ClientNotInOrganizationError()
    if project_id is not None and project_repository.get_for_organization(db, organization_id, project_id) is None:
        raise ProjectNotInOrganizationError()


def create_quote(db: Session, organization_id: uuid.UUID, data: QuoteCreate) -> Quote:
    _validate_client_and_project(db, organization_id, data.client_id, data.project_id)

    subtotal_cents, total_cents = compute_totals(
        [(li.quantity, li.unit_price_cents) for li in data.line_items], data.tax_rate
    )

    quote = Quote(
        organization_id=organization_id,
        client_id=data.client_id,
        project_id=data.project_id,
        number=generate_number(db, organization_id, "DEV", Quote),
        tax_rate=data.tax_rate,
        valid_until=data.valid_until,
        subtotal_cents=subtotal_cents,
        total_cents=total_cents,
    )
    quote.line_items = [
        QuoteLineItem(description=li.description, quantity=li.quantity, unit_price_cents=li.unit_price_cents, position=i)
        for i, li in enumerate(data.line_items)
    ]
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def update_quote(db: Session, organization_id: uuid.UUID, quote_id: uuid.UUID, data: QuoteUpdate) -> Quote:
    quote = get_quote(db, organization_id, quote_id)
    if quote.status != QuoteStatus.DRAFT:
        raise QuoteLockedError()

    if data.project_id is not None and project_repository.get_for_organization(db, organization_id, data.project_id) is None:
        raise ProjectNotInOrganizationError()

    updates = data.model_dump(exclude_unset=True, exclude={"line_items"})
    for field, value in updates.items():
        setattr(quote, field, value)

    if data.line_items is not None:
        quote.line_items = [
            QuoteLineItem(description=li.description, quantity=li.quantity, unit_price_cents=li.unit_price_cents, position=i)
            for i, li in enumerate(data.line_items)
        ]

    tax_rate = data.tax_rate if data.tax_rate is not None else quote.tax_rate
    line_items_for_calc = data.line_items if data.line_items is not None else quote.line_items
    subtotal_cents, total_cents = compute_totals(
        [(li.quantity, li.unit_price_cents) for li in line_items_for_calc], tax_rate
    )
    quote.subtotal_cents = subtotal_cents
    quote.total_cents = total_cents

    db.commit()
    db.refresh(quote)
    return quote


def transition_quote(db: Session, organization_id: uuid.UUID, quote_id: uuid.UUID, new_status: QuoteStatus) -> Quote:
    quote = get_quote(db, organization_id, quote_id)
    if new_status not in _ALLOWED_TRANSITIONS.get(quote.status, set()):
        raise InvalidTransitionError()

    now = datetime.now(timezone.utc)
    if new_status == QuoteStatus.SENT:
        quote.sent_at = now
    elif new_status == QuoteStatus.ACCEPTED:
        quote.accepted_at = now

    quote.status = new_status
    db.commit()
    db.refresh(quote)
    return quote


def delete_quote(db: Session, organization_id: uuid.UUID, quote_id: uuid.UUID) -> None:
    quote = get_quote(db, organization_id, quote_id)
    if quote.status != QuoteStatus.DRAFT:
        raise QuoteLockedError()
    db.delete(quote)
    db.commit()
