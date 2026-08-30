import uuid

from pydantic import BaseModel, ConfigDict

from app.models.billing import PlanCode


class CheckoutSessionRequest(BaseModel):
    plan_code: PlanCode


class SessionUrlResponse(BaseModel):
    url: str


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: PlanCode
    name: str
    price_cents: int
    max_prospects: int | None
    max_documents_per_month: int | None
    ai_generations_per_month: int | None
