"""Unit tests for the json_path value extractor (Phase 3 Task 2)."""

from __future__ import annotations

from typing import Any

from crosswalk_profiler.extract import ExtractedValue, extract_values


def _values(payload: Any, path: str) -> list[Any]:
    return [ev.value for ev in extract_values(payload, path) if ev.present]


class TestRoot:
    def test_root_returns_whole_payload(self) -> None:
        result = extract_values({"a": 1}, "$")
        assert result == [ExtractedValue.of({"a": 1})]


class TestObjectAccess:
    def test_simple_key(self) -> None:
        assert _values({"claimNumber": "C-100"}, "$.claimNumber") == ["C-100"]

    def test_nested_key(self) -> None:
        payload = {"claimant": {"firstName": "John"}}
        assert _values(payload, "$.claimant.firstName") == ["John"]

    def test_missing_key_is_absent(self) -> None:
        result = extract_values({"a": 1}, "$.b")
        assert result == [ExtractedValue.absent()]
        assert result[0].present is False

    def test_missing_nested_key_is_absent(self) -> None:
        result = extract_values({"claimant": {}}, "$.claimant.firstName")
        assert result[0].present is False

    def test_explicit_null_is_present(self) -> None:
        result = extract_values({"reserve": None}, "$.reserve")
        assert result == [ExtractedValue.of(None)]
        assert result[0].present is True  # null is present, not absent

    def test_descend_into_non_object_is_absent(self) -> None:
        # $.a.b where a is a scalar.
        result = extract_values({"a": 5}, "$.a.b")
        assert result[0].present is False


class TestArrayFanOut:
    def test_array_of_scalars(self) -> None:
        assert _values({"tags": ["x", "y", "z"]}, "$.tags[*]") == ["x", "y", "z"]

    def test_array_of_objects_field(self) -> None:
        payload = {
            "partyInfo": [
                {"roleCd": "CLMT", "firstNm": "John"},
                {"roleCd": "INSD", "firstNm": "Jane"},
            ]
        }
        assert _values(payload, "$.partyInfo[*].roleCd") == ["CLMT", "INSD"]
        assert _values(payload, "$.partyInfo[*].firstNm") == ["John", "Jane"]

    def test_fanout_over_non_list_is_absent(self) -> None:
        result = extract_values({"partyInfo": "not-a-list"}, "$.partyInfo[*].roleCd")
        assert result == [ExtractedValue.absent()]

    def test_empty_array_yields_no_observations(self) -> None:
        result = extract_values({"partyInfo": []}, "$.partyInfo[*].roleCd")
        assert result == []  # empty, not absent

    def test_missing_field_in_some_elements(self) -> None:
        payload = {"items": [{"x": 1}, {"y": 2}, {"x": 3}]}
        result = extract_values(payload, "$.items[*].x")
        present = [ev.value for ev in result if ev.present]
        absent = [ev for ev in result if not ev.present]
        assert present == [1, 3]
        assert len(absent) == 1  # the {"y": 2} element had no x

    def test_nested_arrays(self) -> None:
        payload = {"groups": [{"members": [{"n": "a"}, {"n": "b"}]}, {"members": [{"n": "c"}]}]}
        assert _values(payload, "$.groups[*].members[*].n") == ["a", "b", "c"]


class TestDeepNesting:
    def test_hard_shape(self) -> None:
        payload = {
            "case": {
                "ref": "C-100",
                "involved": [{"given": "John"}, {"given": "Jane"}],
                "ledger": {"inc": "14200.00"},
            }
        }
        assert _values(payload, "$.case.ref") == ["C-100"]
        assert _values(payload, "$.case.involved[*].given") == ["John", "Jane"]
        assert _values(payload, "$.case.ledger.inc") == ["14200.00"]
