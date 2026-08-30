import uuid

from pydantic import BaseModel, Field


class QuoteDraftRequest(BaseModel):
    client_id: uuid.UUID
    # Bornée : protection basique contre l'abus (un prompt énorme coûte cher
    # et n'aide pas un cas d'usage "décrivez le projet en une phrase").
    prompt: str = Field(min_length=3, max_length=500)


class QuoteDraftLineItemOut(BaseModel):
    description: str
    quantity: float
    unit_price_cents: int


class QuoteDraftResponse(BaseModel):
    line_items: list[QuoteDraftLineItemOut]
    suggested_tax_rate: float


class ReminderDraftResponse(BaseModel):
    subject: str
    body: str
