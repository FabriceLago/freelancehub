import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.quote import QuoteStatus


class QuoteLineItemIn(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(default=Decimal(1), gt=0)
    unit_price_cents: int = Field(ge=0)


class QuoteLineItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    description: str
    quantity: Decimal
    unit_price_cents: int
    position: int


class QuoteCreate(BaseModel):
    client_id: uuid.UUID
    project_id: uuid.UUID | None = None
    tax_rate: Decimal = Field(default=Decimal(0), ge=0, le=100)
    valid_until: date | None = None
    line_items: list[QuoteLineItemIn] = Field(min_length=1)


class QuoteUpdate(BaseModel):
    # Modifiable uniquement tant que le devis est en DRAFT (imposé par le
    # service) — un devis envoyé ne doit plus changer silencieusement de
    # montant sous le client.
    project_id: uuid.UUID | None = None
    tax_rate: Decimal | None = Field(default=None, ge=0, le=100)
    valid_until: date | None = None
    line_items: list[QuoteLineItemIn] | None = Field(default=None, min_length=1)


class QuoteTransition(BaseModel):
    status: QuoteStatus


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    number: str
    status: QuoteStatus
    currency: str
    client_id: uuid.UUID
    project_id: uuid.UUID | None
    subtotal_cents: int
    tax_rate: Decimal
    total_cents: int
    valid_until: date | None
    sent_at: datetime | None
    accepted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class QuoteDetailOut(QuoteOut):
    line_items: list[QuoteLineItemOut] = []
