from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Job(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    status: JobStatus = JobStatus.QUEUED
    attempt_count: int = Field(default=0, ge=0)
    progress: int = Field(default=0, ge=0, le=100)
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
