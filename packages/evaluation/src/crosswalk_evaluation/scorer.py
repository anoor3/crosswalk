from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from crosswalk_mapping import MappingCandidate


class EvaluationReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    total: int = Field(ge=0)
    correct: int = Field(ge=0)
    unresolved: int = Field(ge=0)
    accuracy: float = Field(ge=0, le=1)


def evaluate_candidates(
    candidates: tuple[MappingCandidate, ...], expected: dict[str, str | None]
) -> EvaluationReport:
    """Compare candidate paths to an explicit answer key; never infer ground truth."""
    if set(expected) != {candidate.external_path for candidate in candidates}:
        raise ValueError("expected keys must match candidate external paths")
    correct = sum(
        candidate.canonical_path == expected[candidate.external_path] for candidate in candidates
    )
    unresolved = sum(candidate.canonical_path is None for candidate in candidates)
    total = len(candidates)
    return EvaluationReport(
        total=total,
        correct=correct,
        unresolved=unresolved,
        accuracy=correct / total if total else 0,
    )
