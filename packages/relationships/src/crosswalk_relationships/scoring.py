"""Explainable relationship candidate scoring."""

from __future__ import annotations

import re
from collections.abc import Iterable
from math import sqrt

from .errors import InvalidRelationshipInputError
from .models import (
    FieldReference,
    RelationshipCandidate,
    RelationshipEvidence,
    RelationshipStatus,
)
from .overlap import overlap_stats

_WORDS = re.compile(r"[a-z0-9]+")
_ALIASES = {"ref": "id", "identifier": "id", "number": "id", "no": "id", "key": "id"}


def _tokens(value: str) -> frozenset[str]:
    return frozenset(_ALIASES.get(word, word) for word in _WORDS.findall(value.lower()))


def _name_score(source: FieldReference, target: FieldReference) -> float:
    left = _tokens(source.name)
    right = _tokens(target.name)
    if not left or not right:
        return 0.0
    return len(left & right) / sqrt(len(left) * len(right))


def _type_score(source: FieldReference, target: FieldReference) -> float:
    if source.data_type is None or target.data_type is None:
        return 0.5
    return 1.0 if source.data_type == target.data_type else 0.0


def score_relationship(
    source: FieldReference,
    target: FieldReference,
    source_values: Iterable[object],
    target_values: Iterable[object],
    *,
    source_description: str = "",
    target_description: str = "",
) -> RelationshipCandidate:
    """Score one source/target pair from aggregates and field metadata."""
    if source.endpoint == target.endpoint and source.json_path == target.json_path:
        raise InvalidRelationshipInputError("a field cannot relate to itself")
    stats = overlap_stats(source_values, target_values)
    name_score = _name_score(source, target)
    type_score = _type_score(source, target)
    reasons: list[str] = [
        f"{stats.overlap_count} distinct values overlap "
        f"({stats.overlap_rate:.2f} source coverage).",
        f"Normalized field-name similarity is {name_score:.2f}.",
        f"Declared type compatibility is {type_score:.2f}.",
    ]
    if source_description and target_description:
        shared = _tokens(source_description) & _tokens(target_description)
        if shared:
            reasons.append(f"Descriptions share {len(shared)} normalized terms.")
            name_score = min(1.0, name_score + 0.1)
    score = 0.5 * stats.overlap_rate + 0.3 * name_score + 0.2 * type_score
    if stats.overlap_count == 0:
        status = RelationshipStatus.UNRESOLVED
        reasons.append("No observed value overlap supports a relationship.")
    elif score >= 0.8 and stats.overlap_rate >= 0.8 and name_score >= 0.6 and type_score > 0:
        status = RelationshipStatus.HIGH_CONFIDENCE
    elif score >= 0.45:
        status = RelationshipStatus.REVIEW_REQUIRED
        reasons.append("Evidence is plausible but needs human confirmation.")
    else:
        status = RelationshipStatus.UNRESOLVED
        reasons.append("Evidence is too weak to propose a relationship.")
    evidence = RelationshipEvidence(
        source_count=stats.source_count,
        target_count=stats.target_count,
        overlap_count=stats.overlap_count,
        overlap_rate=stats.overlap_rate,
        source_unique_rate=stats.source_unique_rate,
        target_unique_rate=stats.target_unique_rate,
        name_score=name_score,
        type_score=type_score,
        reasons=tuple(reasons),
    )
    return RelationshipCandidate(
        source=source,
        target=target if status is not RelationshipStatus.UNRESOLVED else None,
        score=score,
        status=status,
        cardinality=stats.cardinality,
        evidence=evidence,
    )
