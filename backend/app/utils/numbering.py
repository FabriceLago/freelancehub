import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def generate_number(db: Session, organization_id: uuid.UUID, prefix: str, model) -> str:
    """Numéro lisible du type "DEV-2026-0001". Compteur non remis à zéro
    chaque année (simplification MVP assumée) — juste un ordre de grandeur
    monotone par organisation, pas une numérotation comptable stricte."""
    count = db.execute(
        select(func.count()).select_from(model).where(model.organization_id == organization_id)
    ).scalar_one()
    year = datetime.now(timezone.utc).year
    return f"{prefix}-{year}-{count + 1:04d}"
