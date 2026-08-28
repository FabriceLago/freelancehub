import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.quote import Quote, QuoteStatus


def list_for_organization(db: Session, organization_id: uuid.UUID, status: QuoteStatus | None = None) -> list[Quote]:
    stmt = select(Quote).where(Quote.organization_id == organization_id)
    if status is not None:
        stmt = stmt.where(Quote.status == status)
    stmt = stmt.order_by(Quote.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_for_organization(db: Session, organization_id: uuid.UUID, quote_id: uuid.UUID) -> Quote | None:
    return db.execute(
        select(Quote)
        .options(selectinload(Quote.line_items))
        .where(Quote.id == quote_id, Quote.organization_id == organization_id)
    ).scalar_one_or_none()
