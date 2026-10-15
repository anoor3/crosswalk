"""Privacy-preserving value overlap and cardinality statistics."""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field

from .errors import InvalidRelationshipInputError
from .models import Cardinality


class OverlapStats(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    source_count: int = Field(ge=0)
    target_count: int = Field(ge=0)
    source_unique_count: int = Field(ge=0)
    target_unique_count: int = Field(ge=0)
    overlap_count: int = Field(ge=0)
    overlap_rate: float = Field(ge=0, le=1)
    source_unique_rate: float = Field(ge=0, le=1)
    target_unique_rate: float = Field(ge=0, le=1)
    cardinality: Cardinality


def _normalized(values: Iterable[object], label: str) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, (dict, list, set, tuple)):
            raise InvalidRelationshipInputError(f"{label} contains a non-scalar value")
        text = str(value).strip()
        if text:
            result.append(text)
    return tuple(result)


def overlap_stats(source_values: Iterable[object], target_values: Iterable[object]) -> OverlapStats:
    """Compute counts only; raw identifiers never appear in the result."""
    source = _normalized(source_values, "source_values")
    target = _normalized(target_values, "target_values")
    source_set = set(source)
    target_set = set(target)
    overlap = source_set & target_set
    source_unique_rate = len(source_set) / len(source) if source else 0.0
    target_unique_rate = len(target_set) / len(target) if target else 0.0
    if not source or not target:
        cardinality = Cardinality.UNKNOWN
    elif source_unique_rate >= 0.999 and target_unique_rate >= 0.999:
        cardinality = Cardinality.ONE_TO_ONE
    elif source_unique_rate >= 0.999:
        cardinality = Cardinality.ONE_TO_MANY
    elif target_unique_rate >= 0.999:
        cardinality = Cardinality.MANY_TO_ONE
    else:
        cardinality = Cardinality.MANY_TO_MANY
    return OverlapStats(
        source_count=len(source),
        target_count=len(target),
        source_unique_count=len(source_set),
        target_unique_count=len(target_set),
        overlap_count=len(overlap),
        overlap_rate=len(overlap) / len(source_set) if source_set else 0.0,
        source_unique_rate=source_unique_rate,
        target_unique_rate=target_unique_rate,
        cardinality=cardinality,
    )
