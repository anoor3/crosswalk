"""Unit tests for the profiling engine (Phase 3 Task 3)."""

from __future__ import annotations

from typing import Any

from crosswalk_profiler import (
    ObservedType,
    SemanticType,
    profile_field,
    profile_values,
)
from crosswalk_profiler.extract import ExtractedValue


def _pv(values: list[Any], path: str = "$.x") -> Any:
    """profile_values from a list of present values."""
    return profile_values(path, [ExtractedValue.of(v) for v in values])


class TestCountsAndRates:
    def test_basic_counts(self) -> None:
        p = _pv(["a", "b", "c", "a"])
        assert p.sample_count == 4
        assert p.present_count == 4
        assert p.null_count == 0
        assert p.unique_count == 3
        assert p.unique_rate == 0.75

    def test_null_handling(self) -> None:
        extracted = [
            ExtractedValue.of("a"),
            ExtractedValue.of(None),
            ExtractedValue.absent(),
        ]
        p = profile_values("$.x", extracted)
        assert p.sample_count == 3
        assert p.present_count == 2  # "a" and explicit null
        assert p.null_count == 1
        assert round(p.null_rate, 3) == round(1 / 3, 3)

    def test_empty(self) -> None:
        p = profile_values("$.x", [])
        assert p.sample_count == 0
        assert p.null_rate == 0.0
        assert p.semantic_type is SemanticType.UNKNOWN


class TestObservedTypes:
    def test_bool_not_counted_as_int(self) -> None:
        p = _pv([True, False, True])
        assert p.observed_types == (ObservedType.BOOLEAN,)
        assert p.semantic_type is SemanticType.BOOLEAN

    def test_mixed_types_flagged(self) -> None:
        p = _pv(["a", 1, 2.0])
        assert p.is_mixed_type is True
        assert set(p.observed_types) == {
            ObservedType.STRING,
            ObservedType.INTEGER,
            ObservedType.NUMBER,
        }


class TestNumericStats:
    def test_min_max_mean(self) -> None:
        p = _pv([10, 20, 30])
        assert p.numeric_stats is not None
        assert p.numeric_stats.minimum == 10.0
        assert p.numeric_stats.maximum == 30.0
        assert p.numeric_stats.mean == 20.0

    def test_bool_excluded_from_numeric(self) -> None:
        p = _pv([True, False])
        assert p.numeric_stats is None


class TestStringStats:
    def test_lengths(self) -> None:
        p = _pv(["ab", "abcd", "abcdef"])
        assert p.string_stats is not None
        assert p.string_stats.min_length == 2
        assert p.string_stats.max_length == 6
        assert p.string_stats.mean_length == 4.0


class TestPattern:
    def test_dominant_signature(self) -> None:
        p = _pv(["CLM-100", "CLM-200", "CLM-300"])
        assert p.detected_pattern == "AAA-000"

    def test_no_dominant_pattern(self) -> None:
        p = _pv(["abc", "1234567", "!!"])
        assert p.detected_pattern is None


class TestDateDetection:
    def test_iso_dates(self) -> None:
        p = _pv(["2026-09-04", "2026-07-15", "2026-02-28"])
        assert p.detected_date_format == "%Y-%m-%d"
        assert p.semantic_type is SemanticType.DATE

    def test_us_dates(self) -> None:
        p = _pv(["09/04/26", "07/15/26"])
        assert p.detected_date_format == "%m/%d/%y"
        assert p.semantic_type is SemanticType.DATE

    def test_slashed_iso(self) -> None:
        p = _pv(["2026/09/04", "2026/07/15"])
        assert p.detected_date_format == "%Y/%m/%d"

    def test_mixed_non_dates(self) -> None:
        p = _pv(["2026-09-04", "hello"])
        assert p.detected_date_format is None


class TestSemanticHeuristics:
    def test_identifier(self) -> None:
        # High uniqueness + coded pattern with digits.
        p = _pv(["CLM-100", "CLM-201", "CLM-302", "CLM-403"])
        assert p.semantic_type is SemanticType.IDENTIFIER

    def test_enum_candidate(self) -> None:
        # Low cardinality, repeated, enough samples.
        p = _pv(["OPN", "CLS", "OPN", "PND", "OPN", "CLS"])
        assert p.semantic_type is SemanticType.ENUM_CANDIDATE

    def test_enum_candidate_numeric_codes(self) -> None:
        p = _pv([1, 2, 1, 3, 1, 2])
        assert p.semantic_type is SemanticType.ENUM_CANDIDATE

    def test_currency_two_decimal_strings(self) -> None:
        p = _pv(["10000.00", "4200.00", "22750.50", "9500.00"])
        assert p.semantic_type is SemanticType.CURRENCY

    def test_currency_floats(self) -> None:
        p = _pv([10000.0, 4200.5, 22750.5, 9500.25])
        assert p.semantic_type is SemanticType.CURRENCY

    def test_free_text(self) -> None:
        p = _pv([
            "The quick brown fox",
            "jumps over the lazy dog",
            "another distinct sentence here",
            "and one more different phrase",
        ])
        assert p.semantic_type is SemanticType.FREE_TEXT


class TestProfileFieldAcrossPayloads:
    def test_fanout_across_payloads(self) -> None:
        payloads = [
            {"partyInfo": [{"roleCd": "CLMT"}, {"roleCd": "INSD"}]},
            {"partyInfo": [{"roleCd": "CLMT"}, {"roleCd": "INSD"}]},
        ]
        p = profile_field(payloads, "$.partyInfo[*].roleCd")
        assert p.sample_count == 4
        assert p.unique_count == 2
        assert p.semantic_type is SemanticType.ENUM_CANDIDATE
