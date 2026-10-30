from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=1000)
    trace_id: str = Field(min_length=1)


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: str = Field(pattern=r"^(ok|degraded)$")
    version: str = Field(min_length=1)


class JobResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    status: str = Field(min_length=1)
    progress: int = Field(ge=0, le=100)


class JobStatusResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    status: str = Field(min_length=1)


class TenantJobLookup(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str = Field(min_length=1)
    job_id: str = Field(min_length=1)


class CreateJobRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)


class CancelJobRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str = Field(min_length=1)


class ServiceInfoResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    environment: str = Field(min_length=1)


class EventResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="allow")

    event: str = Field(min_length=1)


class Page[T](BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    items: tuple[T, ...]
    next_cursor: str | None = None
