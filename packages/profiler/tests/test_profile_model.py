"""Unit tests for the FieldProfile data model (Phase 3 Task 1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from crosswalk_profiler import (
    FieldProfile,
    NumericStats,
    ObservedType,
    SemanticType,
)


def _profile(**overrides: object) -> FieldProfile:
    data: dict[str, object] = {
        "json_path": "$.lossNo",
        "sample_count": 4,
        "present_count": 4,
        "null_count": 0,
        "null_rate": 0.0,
        "unique_count": 4,
        "unique_rate": 1.0,
        "observed_types": (ObservedType.STRING,),
    }
    data.update(overrides)
    return FieldProfile(**data)  # type: ignore[arg-type]


class TestFieldProfile:
    def test_minimal(self) -> None:
        p = _profile()
        assert p.semantic_type is SemanticType.UNKNOWN
        assert p.numeric_stats is None
        assert p.sample_values == ()

    def test_numeric_stats(self) -> None:
        p = _profile(numeric_stats=NumericStats(minimum=0.0, maximum=10.0, mean=5.0))
        assert p.numeric_stats is not None
        assert p.numeric_stats.mean == 5.0

    def test_frozen(self) -> None:
        p = _profile()
        with pytest.raises(ValidationError):
            p.json_path = "$.other"  # type: ignore[misc]

    def test_unknown_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            _profile(bogus=1)
