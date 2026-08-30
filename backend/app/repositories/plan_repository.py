from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.billing import Plan, PlanCode


def list_all(db: Session) -> list[Plan]:
    return list(db.execute(select(Plan).order_by(Plan.price_cents)).scalars().all())


def get_by_code(db: Session, code: PlanCode) -> Plan | None:
    return db.execute(select(Plan).where(Plan.code == code)).scalar_one_or_none()


def get_by_stripe_price_id(db: Session, price_id: str) -> Plan | None:
    return db.execute(select(Plan).where(Plan.stripe_price_id == price_id)).scalar_one_or_none()
