import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.invoice import Invoice, InvoiceLineItem, InvoiceStatus, Payment
from app.models.quote import Quote
from app.repositories import client_repository, invoice_repository, project_repository
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.utils.money import compute_totals
from app.utils.numbering import generate_number


class InvoiceNotFoundError(AppError):
    pass


class ClientNotInOrganizationError(AppError):
    pass


class ProjectNotInOrganizationError(AppError):
    pass


class InvoiceLockedError(AppError):
    """La facture n'est plus en DRAFT : montants et lignes ne peuvent plus changer."""


class InvalidTransitionError(AppError):
    pass


class AlreadyPaidError(AppError):
    pass


# PAID n'apparaît volontairement pas ici : seul mark_paid() peut y mener,
# parce que passer PAID crée un vrai Payment — un simple changement de
# statut ne suffit pas à représenter "de l'argent a été reçu".
_ALLOWED_TRANSITIONS: dict[InvoiceStatus, set[InvoiceStatus]] = {
    InvoiceStatus.DRAFT: {InvoiceStatus.SENT, InvoiceStatus.CANCELLED},
    InvoiceStatus.SENT: {InvoiceStatus.CANCELLED},
}


def list_invoices(db: Session, organization_id: uuid.UUID, status: InvoiceStatus | None) -> list[Invoice]:
    return invoice_repository.list_for_organization(db, organization_id, status)


def get_invoice(db: Session, organization_id: uuid.UUID, invoice_id: uuid.UUID) -> Invoice:
    invoice = invoice_repository.get_for_organization(db, organization_id, invoice_id)
    if invoice is None:
        raise InvoiceNotFoundError()
    return invoice


def _validate_client_and_project(db: Session, organization_id: uuid.UUID, client_id: uuid.UUID, project_id) -> None:
    if client_repository.get_for_organization(db, organization_id, client_id) is None:
        raise ClientNotInOrganizationError()
    if project_id is not None and project_repository.get_for_organization(db, organization_id, project_id) is None:
        raise ProjectNotInOrganizationError()


def create_invoice(db: Session, organization_id: uuid.UUID, data: InvoiceCreate) -> Invoice:
    _validate_client_and_project(db, organization_id, data.client_id, data.project_id)

    subtotal_cents, total_cents = compute_totals(
        [(li.quantity, li.unit_price_cents) for li in data.line_items], data.tax_rate
    )

    invoice = Invoice(
        organization_id=organization_id,
        client_id=data.client_id,
        project_id=data.project_id,
        number=generate_number(db, organization_id, "FAC", Invoice),
        tax_rate=data.tax_rate,
        due_date=data.due_date,
        subtotal_cents=subtotal_cents,
        total_cents=total_cents,
    )
    invoice.line_items = [
        InvoiceLineItem(description=li.description, quantity=li.quantity, unit_price_cents=li.unit_price_cents, position=i)
        for i, li in enumerate(data.line_items)
    ]
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def create_invoice_from_quote(db: Session, organization_id: uuid.UUID, quote: Quote) -> Invoice:
    """Copie les lignes/montants d'un devis ACCEPTED vers une nouvelle facture
    DRAFT, liée via quote_id. La validation "devis bien ACCEPTED" est faite
    par l'appelant (app/api/quotes.py), pas ici : ce service ne connaît que
    la mécanique de copie, pas les règles de cycle de vie du devis."""
    invoice = Invoice(
        organization_id=organization_id,
        client_id=quote.client_id,
        project_id=quote.project_id,
        quote_id=quote.id,
        number=generate_number(db, organization_id, "FAC", Invoice),
        tax_rate=quote.tax_rate,
        subtotal_cents=quote.subtotal_cents,
        total_cents=quote.total_cents,
    )
    invoice.line_items = [
        InvoiceLineItem(description=li.description, quantity=li.quantity, unit_price_cents=li.unit_price_cents, position=li.position)
        for li in quote.line_items
    ]
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def update_invoice(db: Session, organization_id: uuid.UUID, invoice_id: uuid.UUID, data: InvoiceUpdate) -> Invoice:
    invoice = get_invoice(db, organization_id, invoice_id)
    if invoice.status != InvoiceStatus.DRAFT:
        raise InvoiceLockedError()

    if data.project_id is not None and project_repository.get_for_organization(db, organization_id, data.project_id) is None:
        raise ProjectNotInOrganizationError()

    updates = data.model_dump(exclude_unset=True, exclude={"line_items"})
    for field, value in updates.items():
        setattr(invoice, field, value)

    if data.line_items is not None:
        invoice.line_items = [
            InvoiceLineItem(description=li.description, quantity=li.quantity, unit_price_cents=li.unit_price_cents, position=i)
            for i, li in enumerate(data.line_items)
        ]

    tax_rate = data.tax_rate if data.tax_rate is not None else invoice.tax_rate
    line_items_for_calc = data.line_items if data.line_items is not None else invoice.line_items
    subtotal_cents, total_cents = compute_totals(
        [(li.quantity, li.unit_price_cents) for li in line_items_for_calc], tax_rate
    )
    invoice.subtotal_cents = subtotal_cents
    invoice.total_cents = total_cents

    db.commit()
    db.refresh(invoice)
    return invoice


def transition_invoice(
    db: Session, organization_id: uuid.UUID, invoice_id: uuid.UUID, new_status: InvoiceStatus
) -> Invoice:
    invoice = get_invoice(db, organization_id, invoice_id)
    if new_status not in _ALLOWED_TRANSITIONS.get(invoice.status, set()):
        raise InvalidTransitionError()

    if new_status == InvoiceStatus.SENT:
        invoice.sent_at = datetime.now(timezone.utc)

    invoice.status = new_status
    db.commit()
    db.refresh(invoice)
    return invoice


def mark_paid(db: Session, organization_id: uuid.UUID, invoice_id: uuid.UUID) -> Invoice:
    """Encaisse le solde restant en une fois (paiement partiel : hors scope
    MVP, voir schémas). Crée un vrai Payment plutôt que de juste basculer
    un statut — cohérent avec le commentaire du modèle Invoice (Étape 3)."""
    invoice = get_invoice(db, organization_id, invoice_id)
    if invoice.status == InvoiceStatus.PAID:
        raise AlreadyPaidError()

    now = datetime.now(timezone.utc)
    db.add(Payment(invoice_id=invoice.id, amount_cents=invoice.balance_cents, method="manual", paid_at=now))
    invoice.status = InvoiceStatus.PAID
    invoice.paid_at = now
    db.commit()
    db.refresh(invoice)
    return invoice


def delete_invoice(db: Session, organization_id: uuid.UUID, invoice_id: uuid.UUID) -> None:
    invoice = get_invoice(db, organization_id, invoice_id)
    if invoice.status != InvoiceStatus.DRAFT:
        raise InvoiceLockedError()
    db.delete(invoice)
    db.commit()
