from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    event_type: str = Field(min_length=1)
    actor_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    occurred_at: datetime
    summary: str = Field(min_length=1, max_length=1000)
