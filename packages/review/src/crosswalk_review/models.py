"""Immutable records for human mapping review.

Review records contain concise evidence and decisions, never hidden model
reasoning or raw payloads. A record is an auditable snapshot; every decision
appends a new version instead of mutating history.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from crosswalk_mapping import MappingCandidate

_CONFIG = ConfigDict(frozen=True, extra="forbid")


class ReviewState(StrEnum):
    OPEN = "OPEN"
    CONFIRMED = "CONFIRMED"
    CORRECTED = "CORRECTED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class ReviewActionType(StrEnum):
    CONFIRM = "CONFIRM"
    CORRECT = "CORRECT"
    REJECT = "REJECT"
    LEAVE_UNRESOLVED = "LEAVE_UNRESOLVED"


class ReviewAction(BaseModel):
    """One reviewer decision, retained permanently in record history."""

    model_config = _CONFIG

    version: int = Field(ge=1)
    action: ReviewActionType
    reviewer_id: str = Field(min_length=1)
    canonical_path: str | None = None
    rationale: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def _action_target_consistency(self) -> Self:
        needs_target = self.action in (ReviewActionType.CONFIRM, ReviewActionType.CORRECT)
        if needs_target and not self.canonical_path:
            raise ValueError("confirm and correct require a canonical target")
        if not needs_target and self.canonical_path is not None:
            raise ValueError("reject and leave-unresolved cannot select a target")
        return self


class ReviewRecord(BaseModel):
    """Current review state plus immutable decision history."""

    model_config = _CONFIG

    review_id: str = Field(min_length=1)
    external_path: str = Field(min_length=1)
    candidate: MappingCandidate
    state: ReviewState = ReviewState.OPEN
    canonical_path: str | None = None
    version: int = Field(default=0, ge=0)
    actions: tuple[ReviewAction, ...] = ()

    @model_validator(mode="after")
    def _state_consistency(self) -> Self:
        if self.version != len(self.actions):
            raise ValueError("version must equal the number of recorded actions")
        if self.external_path != self.candidate.external_path:
            raise ValueError("record path must match its candidate")
        if self.state in (ReviewState.CONFIRMED, ReviewState.CORRECTED) and not self.canonical_path:
            raise ValueError("confirmed and corrected records require a target")
        if self.state in (ReviewState.REJECTED, ReviewState.UNRESOLVED) and self.canonical_path:
            raise ValueError("rejected and unresolved records cannot have a target")
        if self.actions and self.actions[-1].version != self.version:
            raise ValueError("last action version must match record version")
        return self


class EvaluationExample(BaseModel):
    """A reviewed source/target pair suitable for a later evaluation set."""

    model_config = _CONFIG

    external_path: str = Field(min_length=1)
    canonical_path: str = Field(min_length=1)
    review_id: str = Field(min_length=1)
    review_version: int = Field(ge=1)
    reviewer_id: str = Field(min_length=1)
    rationale: str = Field(min_length=1, max_length=2000)
