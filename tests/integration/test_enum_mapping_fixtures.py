"""Phase 6 enum mapping over real samples, without hidden annotations."""

import json
from pathlib import Path

import pytest
from crosswalk_enum_mapping import (
    EnumMappingStatus,
    UnknownEnumValueError,
    map_enum_values,
    translate_enum,
)

from crosswalk_canonical import ClaimStatus
from crosswalk_profiler import profile_field

_PATHS = {"easy": "$.status", "medium": "$.stateCd", "hard": "$.case.state"}


def _values(fixtures_dir: Path, api: str) -> tuple[str, ...]:
    payloads = json.loads((fixtures_dir / "payloads" / api / "claims.json").read_text())
    return profile_field(payloads, _PATHS[api]).sample_values


@pytest.mark.parametrize("api", ["easy", "medium", "hard"])
def test_real_fixture_values_are_all_accounted_for(fixtures_dir: Path, api: str) -> None:
    values = _values(fixtures_dir, api)
    result = map_enum_values(
        values, tuple(status.value for status in ClaimStatus), observed_values=values
    )
    assert result.unseen_values == ()
    assert {item.external_value for item in result.mappings} == set(values)


def test_easy_status_values_translate_without_external_codes(fixtures_dir: Path) -> None:
    values = _values(fixtures_dir, "easy")
    result = map_enum_values(values, tuple(status.value for status in ClaimStatus))
    assert all(item.status is EnumMappingStatus.HIGH_CONFIDENCE for item in result.mappings)
    assert {translate_enum(result, value) for value in values} == set(values)


def test_medium_abbreviations_translate_deterministically(fixtures_dir: Path) -> None:
    values = _values(fixtures_dir, "medium")
    result = map_enum_values(values, tuple(status.value for status in ClaimStatus))
    assert all(item.status is EnumMappingStatus.HIGH_CONFIDENCE for item in result.mappings)
    assert translate_enum(result, "OPN") == "OPEN"
    assert translate_enum(result, "CLS") == "CLOSED"


def test_hard_numeric_codes_remain_unknown_without_evidence(fixtures_dir: Path) -> None:
    values = _values(fixtures_dir, "hard")
    result = map_enum_values(values, tuple(status.value for status in ClaimStatus))
    assert all(item.status is EnumMappingStatus.UNKNOWN for item in result.mappings)
    with pytest.raises(UnknownEnumValueError):
        translate_enum(result, values[0])


def test_new_observed_status_is_explicitly_unseen(fixtures_dir: Path) -> None:
    values = _values(fixtures_dir, "medium")
    result = map_enum_values(
        values,
        tuple(status.value for status in ClaimStatus),
        observed_values=(*values, "ESCALATED"),
    )
    assert result.unseen_values == ("ESCALATED",)
    with pytest.raises(UnknownEnumValueError):
        translate_enum(result, "ESCALATED")
