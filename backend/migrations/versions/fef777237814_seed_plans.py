"""seed plans

Revision ID: fef777237814
Revises: 2954b578eec7
Create Date: 2026-08-28 22:53:23.209539

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fef777237814'
down_revision: Union[str, Sequence[str], None] = '2954b578eec7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# IDs fixes (pas uuid4 aléatoire) : une migration doit être reproductible à
# l'identique sur chaque environnement (dev/staging/prod).
PLAN_IDS = {
    "free": uuid.UUID("00000000-0000-0000-0000-000000000001"),
    "starter": uuid.UUID("00000000-0000-0000-0000-000000000002"),
    "pro": uuid.UUID("00000000-0000-0000-0000-000000000003"),
    "business": uuid.UUID("00000000-0000-0000-0000-000000000004"),
}

plans_table = sa.table(
    "plans",
    sa.column("id", sa.Uuid),
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("price_cents", sa.Integer),
    sa.column("max_prospects", sa.Integer),
    sa.column("max_documents_per_month", sa.Integer),
    sa.column("ai_generations_per_month", sa.Integer),
)


def upgrade() -> None:
    op.bulk_insert(
        plans_table,
        [
            {
                "id": PLAN_IDS["free"],
                "code": "free",
                "name": "Free",
                "price_cents": 0,
                "max_prospects": 3,
                "max_documents_per_month": 2,
                "ai_generations_per_month": 0,
            },
            {
                "id": PLAN_IDS["starter"],
                "code": "starter",
                "name": "Starter",
                "price_cents": 900,
                "max_prospects": None,
                "max_documents_per_month": 15,
                "ai_generations_per_month": 5,
            },
            {
                "id": PLAN_IDS["pro"],
                "code": "pro",
                "name": "Pro",
                "price_cents": 1900,
                "max_prospects": None,
                "max_documents_per_month": None,
                "ai_generations_per_month": None,
            },
            {
                "id": PLAN_IDS["business"],
                "code": "business",
                "name": "Business",
                "price_cents": 3900,
                "max_prospects": None,
                "max_documents_per_month": None,
                "ai_generations_per_month": None,
            },
        ],
    )


def downgrade() -> None:
    op.execute(plans_table.delete().where(plans_table.c.id.in_(list(PLAN_IDS.values()))))
