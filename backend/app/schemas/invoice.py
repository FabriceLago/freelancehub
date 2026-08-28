import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.invoice import InvoiceStatus


class InvoiceLineItemIn(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(default=Decimal(1), gt=0)
    unit_price_cents: int = Field(ge=0)


class InvoiceLineItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    description: str
    quantity: Decimal
    unit_price_cents: int
    position: int


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    amount_cents: int
    method: str
    paid_at: datetime


class InvoiceCreate(BaseModel):
    client_id: uuid.UUID
    project_id: uuid.UUID | None = None
    tax_rate: Decimal = Field(default=Decimal(0), ge=0, le=100)
    due_date: date | None = None
    line_items: list[InvoiceLineItemIn] = Field(min_length=1)


class InvoiceUpdate(BaseModel):
    project_id: uuid.UUID | None = None
    tax_rate: Decimal | None = Field(default=None, ge=0, le=100)
    due_date: date | None = None
    line_items: list[InvoiceLineItemIn] | None = Field(default=None, min_length=1)


class InvoiceTransition(BaseModel):
    status: InvoiceStatus


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    number: str
    status: InvoiceStatus
    currency: str
    client_id: uuid.UUID
    project_id: uuid.UUID | None
    quote_id: uuid.UUID | None
    subtotal_cents: int
    tax_rate: Decimal
    total_cents: int
    paid_cents: int
    balance_cents: int
    due_date: date | None
    sent_at: datetime | None
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime


class InvoiceDetailOut(InvoiceOut):
    line_items: list[InvoiceLineItemOut] = []
    payments: list[PaymentOut] = []
