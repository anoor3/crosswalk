"""Overlap and cardinality tests never assert or print raw identifiers."""

import pytest
from crosswalk_relationships import Cardinality, InvalidRelationshipInputError, overlap_stats


def test_one_to_one_overlap() -> None:
    stats = overlap_stats(["a", "b", "c"], ["a", "b", "c"])
    assert stats.overlap_count == 3
    assert stats.overlap_rate == 1.0
    assert stats.source_unique_rate == 1.0
    assert stats.cardinality is Cardinality.ONE_TO_ONE


def test_one_to_many_cardinality() -> None:
    stats = overlap_stats(["claim-1", "claim-2"], ["claim-1", "claim-1", "claim-2"])
    assert stats.cardinality is Cardinality.ONE_TO_MANY
    assert stats.overlap_count == 2


def test_many_to_one_cardinality() -> None:
    stats = overlap_stats(["person-1", "person-1", "person-2"], ["person-1", "person-2"])
    assert stats.cardinality is Cardinality.MANY_TO_ONE


def test_many_to_many_cardinality() -> None:
    stats = overlap_stats(["a", "a", "b"], ["a", "a", "b", "b"])
    assert stats.cardinality is Cardinality.MANY_TO_MANY


def test_nulls_and_empty_inputs_are_safe() -> None:
    stats = overlap_stats([None, "a", ""], [None])
    assert stats.source_count == 1
    assert stats.target_count == 0
    assert stats.cardinality is Cardinality.UNKNOWN
    assert overlap_stats([], []).overlap_rate == 0.0


@pytest.mark.parametrize("bad", [[{"id": 1}], [["nested"]], [{"x": 1}]])
def test_nested_values_are_rejected(bad: list[object]) -> None:
    with pytest.raises(InvalidRelationshipInputError):
        overlap_stats(bad, ["id"])


def test_numeric_and_string_ids_use_stable_text_form() -> None:
    stats = overlap_stats([1, 2], ["1", "3"])
    assert stats.overlap_count == 1
    assert stats.overlap_rate == 0.5


def test_results_contain_aggregates_only() -> None:
    stats = overlap_stats(["SECRET-ID-123"], ["SECRET-ID-123"])
    payload = stats.model_dump_json()
    assert "SECRET-ID-123" not in payload
    assert stats.overlap_count == 1
