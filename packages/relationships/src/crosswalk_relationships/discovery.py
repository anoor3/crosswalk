"""Wire profiler path extraction into relationship scoring."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from crosswalk_profiler import extract_values

from .models import FieldReference, RelationshipCandidate
from .scoring import score_relationship


def _values(payloads: Iterable[Any], path: str) -> list[object]:
    values: list[object] = []
    for payload in payloads:
        values.extend(
            item.value
            for item in extract_values(payload, path)
            if item.present and item.value is not None
        )
    return values


def discover_relationship(
    source: FieldReference,
    target: FieldReference,
    source_payloads: Sequence[Any],
    target_payloads: Sequence[Any],
    *,
    source_description: str = "",
    target_description: str = "",
) -> RelationshipCandidate:
    """Discover one relationship from payloads addressed by discovered paths."""
    return score_relationship(
        source,
        target,
        _values(source_payloads, source.json_path),
        _values(target_payloads, target.json_path),
        source_description=source_description,
        target_description=target_description,
    )
