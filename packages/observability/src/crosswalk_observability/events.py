from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    trace_id: str = Field(min_length=1)
    tenant_id: str | None = None
    occurred_at: datetime
    attributes: dict[str, str] = {}


class Metric(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    value: float
    unit: str = Field(min_length=1)
    labels: dict[str, str] = {}


def new_trace_id() -> str:
    return uuid4().hex


def event(name: str, trace_id: str, tenant_id: str | None = None) -> Event:
    return Event(name=name, trace_id=trace_id, tenant_id=tenant_id, occurred_at=datetime.now(UTC))
