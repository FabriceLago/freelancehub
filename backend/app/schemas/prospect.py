import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.crm import ProspectStatus


class ProspectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class ProspectUpdate(BaseModel):
    # Tous les champs optionnels : PATCH partiel. `status` exclut volontairement
    # CONVERTED — passer par POST /prospects/{id}/convert, seul endpoint qui
    # crée le Client associé (voir prospect_service.update_status).
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    status: ProspectStatus | None = None


class ProspectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str | None
    phone: str | None
    status: ProspectStatus
    source: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
