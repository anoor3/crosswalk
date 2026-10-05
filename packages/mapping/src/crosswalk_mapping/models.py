"""Mapping hypotheses, with reproducible heuristic scores (not probabilities)."""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from crosswalk_discovery import FieldType
from crosswalk_profiler import SemanticType

_CONFIG = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class MappingStatus(StrEnum):
    """Only a later human review workflow can confirm or reject a mapping."""

    CONFIRMED = "CONFIRMED"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    CONFLICTING = "CONFLICTING"
    UNRESOLVED = "UNRESOLVED"
    REJECTED = "REJECTED"


class CanonicalField(BaseModel):
    """A scalar target; callers may supply their own canonical vocabulary."""

    model_config = _CONFIG

    path: str = Field(min_length=1)
    name: str = Field(min_length=1)
    data_type: FieldType
    description: str = ""
    semantic_type: SemanticType = SemanticType.UNKNOWN
    nullable: bool = False
    enum_values: tuple[str, ...] = ()


class SignalEvidence(BaseModel):
    """None means unavailable, whereas zero is observed lack of support."""

    model_config = _CONFIG

    score: float | None = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1)


class MappingEvidence(BaseModel):
    model_config = _CONFIG

    name: SignalEvidence
    description: SignalEvidence
    type: SignalEvidence
    value_profile: SignalEvidence

    @property
    def score(self) -> float:
        """Weighted mean over available signals; missing evidence is not zero."""
        signals = (self.name, self.description, self.type, self.value_profile)
        available = [signal for signal in signals if signal.score is not None]
        denominator = sum(signal.weight for signal in available)
        if not denominator:
            return 0.0
        return sum((signal.score or 0) * signal.weight for signal in available) / denominator


class MappingAlternative(BaseModel):
    model_config = _CONFIG

    canonical_path: str = Field(min_length=1)
    score: float = Field(ge=0, le=1)
    evidence: MappingEvidence

    @model_validator(mode="after")
    def _score_matches_evidence(self) -> Self:
        if not math.isclose(self.score, self.evidence.score, abs_tol=1e-12):
            raise ValueError("score must equal the weighted evidence score")
        return self


class MappingCandidate(BaseModel):
    """One result per source field, including fields with no proposed target.

    HIGH_CONFIDENCE means a strong ranking under the stated heuristic rules,
    never an approved mapping or a calibrated probability of correctness.
    Alternatives contain the full ranked target list when unresolved; otherwise
    they contain every target except the proposed one. No samples are retained.
    """

    model_config = _CONFIG

    external_path: str = Field(min_length=1)
    canonical_path: str | None
    score: float = Field(ge=0, le=1)
    status: MappingStatus
    evidence: MappingEvidence | None
    alternatives: tuple[MappingAlternative, ...] = ()
    reasons: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _consistent_result(self) -> Self:
        expected = self.evidence.score if self.evidence is not None else 0.0
        if not math.isclose(self.score, expected, abs_tol=1e-12):
            raise ValueError("score must equal the weighted evidence score")
        if self.canonical_path is None and self.status != MappingStatus.UNRESOLVED:
            raise ValueError("a result without a target must be UNRESOLVED")
        if self.status == MappingStatus.UNRESOLVED and self.canonical_path is not None:
            raise ValueError("UNRESOLVED cannot select a target")
        if self.canonical_path is not None and self.evidence is None:
            raise ValueError("a proposed target requires evidence")
        paths = [alternative.canonical_path for alternative in self.alternatives]
        if len(paths) != len(set(paths)) or self.canonical_path in paths:
            raise ValueError("alternatives must be unique and exclude the selected target")
        return self
