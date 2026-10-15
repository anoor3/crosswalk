"""Bounded agent run and audit records."""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_CONFIG = ConfigDict(frozen=True, extra="forbid")


class InvestigationStatus(StrEnum):
    COMPLETED = "COMPLETED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    TIMED_OUT = "TIMED_OUT"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    FAILED = "FAILED"


class ToolCallStatus(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    DENIED = "DENIED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class AgentConfig(BaseModel):
    """Hard limits and permissions for one investigation run."""

    model_config = _CONFIG

    max_iterations: int = Field(default=8, ge=1, le=100)
    timeout_seconds: float = Field(default=30.0, gt=0, le=600)
    token_budget: int = Field(default=10_000, ge=1, le=1_000_000)
    cost_budget_usd: float = Field(default=1.0, ge=0, le=1_000)
    allow_network: bool = False
    allow_production_writes: bool = False

    @model_validator(mode="after")
    def _safe_default(self) -> Self:
        if self.allow_production_writes and not self.allow_network:
            raise ValueError("production writes require an explicitly allowed network")
        return self


class ToolCallRecord(BaseModel):
    model_config = _CONFIG

    iteration: int = Field(ge=1)
    tool_name: str = Field(min_length=1)
    status: ToolCallStatus
    request_summary: str = Field(min_length=1, max_length=1000)
    response_summary: str = Field(min_length=1, max_length=2000)
    latency_ms: float = Field(ge=0)
    estimated_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0, ge=0)


class InvestigationResult(BaseModel):
    model_config = _CONFIG

    goal: str = Field(min_length=1, max_length=2000)
    status: InvestigationStatus
    rationale: str = Field(min_length=1, max_length=4000)
    proposed_mapping: str | None = None
    unresolved_questions: tuple[str, ...] = ()
    tool_history: tuple[ToolCallRecord, ...] = ()
    iterations: int = Field(ge=0)
    estimated_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0, ge=0)
