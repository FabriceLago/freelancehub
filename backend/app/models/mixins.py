import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column


def str_enum(enum_cls: type[enum.Enum], length: int) -> Enum:
    """Enum(native_enum=False) stocke le NOM du membre ('FREE') par défaut,
    pas sa valeur ('free') — piège classique de SQLAlchemy. Comme nos enums
    sont des `str, Enum` dont la valeur EST la forme qu'on veut en base
    (lisible, stable si on renomme un membre Python), on force values_callable
    à utiliser .value partout plutôt que de le refaire à la main 8 fois."""
    return Enum(enum_cls, native_enum=False, length=length, values_callable=lambda x: [e.value for e in x])


class UUIDPrimaryKeyMixin:
    # Uuid (générique SQLAlchemy 2.0) plutôt que postgresql.UUID : compile en
    # UUID natif sur Postgres et reste testable sur SQLite en local.
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
