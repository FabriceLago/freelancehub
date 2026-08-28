import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    company: str | None
    email: str | None
    phone: str | None
    converted_from_prospect_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
