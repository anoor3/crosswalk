"""Inspectable enum mapping results and safe translation contracts."""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

_CONFIG = ConfigDict(frozen=True, extra="forbid")


class EnumMappingStatus(StrEnum):
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class EnumValueCandidate(BaseModel):
    """One external enum value and its canonical hypothesis."""

    model_config = _CONFIG

    external_value: str = Field(min_length=1)
    canonical_value: str | None = None
    score: float = Field(ge=0, le=1)
    status: EnumMappingStatus
    evidence: tuple[str, ...] = ()
    alternatives: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _state_consistency(self) -> Self:
        needs_target = self.status in (
            EnumMappingStatus.HIGH_CONFIDENCE,
            EnumMappingStatus.CONFIRMED,
            EnumMappingStatus.REVIEW_REQUIRED,
            EnumMappingStatus.CONFLICTING,
        )
        if needs_target and self.canonical_value is None:
            raise ValueError("mapped or conflicting enum candidates require a target")
        if self.status is EnumMappingStatus.UNKNOWN and self.canonical_value is not None:
            raise ValueError("unknown enum values cannot select a target")
        if self.status is EnumMappingStatus.REJECTED and self.canonical_value is not None:
            raise ValueError("rejected enum values cannot select a target")
        if self.canonical_value in self.alternatives:
            raise ValueError("alternatives cannot include the selected target")
        return self


class EnumMappingResult(BaseModel):
    """Complete mapping for a declared enum vocabulary and observed values."""

    model_config = _CONFIG

    external_values: tuple[str, ...]
    canonical_values: tuple[str, ...]
    mappings: tuple[EnumValueCandidate, ...]
    unseen_values: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _complete_and_unique(self) -> Self:
        if len(set(self.external_values)) != len(self.external_values):
            raise ValueError("external enum values must be unique")
        if len(set(self.canonical_values)) != len(self.canonical_values):
            raise ValueError("canonical enum values must be unique")
        by_external = [mapping.external_value for mapping in self.mappings]
        if set(by_external) != set(self.external_values) or len(by_external) != len(
            set(by_external)
        ):
            raise ValueError("each declared external value needs exactly one mapping")
        if len(set(self.unseen_values)) != len(self.unseen_values):
            raise ValueError("unseen values must be unique")
        return self

    def candidate(self, external_value: str | int) -> EnumValueCandidate | None:
        value = str(external_value)
        return next((item for item in self.mappings if item.external_value == value), None)
