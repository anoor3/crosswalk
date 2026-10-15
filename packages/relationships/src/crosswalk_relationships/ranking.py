"""Deterministic ranking across competing relationship targets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .errors import DuplicateRelationshipError, InvalidRelationshipInputError
from .models import (
    Cardinality,
    FieldReference,
    RelationshipAlternative,
    RelationshipCandidate,
    RelationshipStatus,
)
from .scoring import score_relationship


def rank_relationships(
    source: FieldReference,
    targets: Sequence[FieldReference],
    source_values: Sequence[object],
    target_values: Mapping[tuple[str, str], Sequence[object]],
) -> RelationshipCandidate:
    """Rank candidate targets and retain close alternatives for review."""
    if not targets:
        return RelationshipCandidate(
            source=source,
            target=None,
            score=0.0,
            status=RelationshipStatus.UNRESOLVED,
            cardinality=Cardinality.UNKNOWN,
            evidence=None,
        )
    keys = [(target.endpoint, target.json_path) for target in targets]
    if len(keys) != len(set(keys)):
        raise DuplicateRelationshipError("relationship targets must be unique")
    missing = [
        target for target in targets if (target.endpoint, target.json_path) not in target_values
    ]
    if missing:
        raise InvalidRelationshipInputError("target values are missing for one or more candidates")
    candidates = [
        score_relationship(
            source, target, source_values, target_values[(target.endpoint, target.json_path)]
        )
        for target in targets
    ]
    candidates.sort(key=lambda item: (-item.score, item.target.json_path if item.target else ""))
    best = candidates[0]
    alternatives = tuple(
        RelationshipAlternative(target=item.target, score=item.score, evidence=item.evidence)
        for item in candidates[1:]
        if item.target is not None and item.evidence is not None
    )
    if best.target is None or best.evidence is None:
        return best.model_copy(update={"alternatives": alternatives})
    if len(candidates) > 1 and best.score - candidates[1].score < 0.1:
        best = best.model_copy(
            update={
                "status": RelationshipStatus.CONFLICTING,
                "alternatives": alternatives,
            }
        )
    else:
        best = best.model_copy(update={"alternatives": alternatives})
    return best
