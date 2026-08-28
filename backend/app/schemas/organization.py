import uuid

from pydantic import BaseModel, ConfigDict

from app.models.organization import Role


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    currency: str
    role: Role
