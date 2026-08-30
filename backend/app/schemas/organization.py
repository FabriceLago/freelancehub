import uuid

from pydantic import BaseModel, ConfigDict

from app.models.billing import PlanCode, SubscriptionStatus
from app.models.organization import Role


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    currency: str
    role: Role
    plan: PlanCode
    subscription_status: SubscriptionStatus
