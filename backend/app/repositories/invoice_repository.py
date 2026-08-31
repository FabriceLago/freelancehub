import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.invoice import Invoice, InvoiceStatus

# Voir prospect_repository._MAX_RESULTS — même filet de sécurité en attendant
# une vraie pagination.
_MAX_RESULTS = 200


def list_for_organization(
    db: Session, organization_id: uuid.UUID, status: InvoiceStatus | None = None
) -> list[Invoice]:
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.payments))
        .where(Invoice.organization_id == organization_id)
    )
    if status is not None:
        stmt = stmt.where(Invoice.status == status)
    stmt = stmt.order_by(Invoice.created_at.desc()).limit(_MAX_RESULTS)
    return list(db.execute(stmt).scalars().all())


def get_for_organization(db: Session, organization_id: uuid.UUID, invoice_id: uuid.UUID) -> Invoice | None:
    return db.execute(
        select(Invoice)
        .options(selectinload(Invoice.line_items), selectinload(Invoice.payments))
        .where(Invoice.id == invoice_id, Invoice.organization_id == organization_id)
    ).scalar_one_or_none()
