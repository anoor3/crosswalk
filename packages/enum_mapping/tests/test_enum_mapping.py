"""Phase 6 enum safety and translation tests."""

import pytest
from crosswalk_enum_mapping import (
    EnumMappingStatus,
    InvalidEnumVocabularyError,
    UnapprovedEnumMappingError,
    UnknownEnumValueError,
    map_enum_values,
    translate_enum,
)
from pydantic import ValidationError

CANONICAL = ("OPEN", "PENDING", "CLOSED", "REOPENED")


def test_exact_values_are_high_confidence_and_translate() -> None:
    result = map_enum_values(CANONICAL, CANONICAL, observed_values=["OPEN", "CLOSED"])
    assert all(item.status is EnumMappingStatus.HIGH_CONFIDENCE for item in result.mappings)
    assert translate_enum(result, "OPEN") == "OPEN"
    assert result.unseen_values == ()


def test_abbreviations_are_explicitly_normalized() -> None:
    result = map_enum_values(("OPN", "PND", "CLS", "RPN"), CANONICAL)
    assert [item.canonical_value for item in result.mappings] == list(CANONICAL)
    assert all(item.status is EnumMappingStatus.HIGH_CONFIDENCE for item in result.mappings)
    assert translate_enum(result, "OPN") == "OPEN"


def test_numeric_codes_without_evidence_remain_unknown() -> None:
    result = map_enum_values((1, 2, 3, 4), CANONICAL, observed_values=[1, 2, 4])
    assert all(item.status is EnumMappingStatus.UNKNOWN for item in result.mappings)
    assert result.unseen_values == ()
    with pytest.raises(UnknownEnumValueError):
        translate_enum(result, 1)


def test_explicit_mapping_is_confirmed_and_numeric_codes_can_be_translated() -> None:
    result = map_enum_values(
        (1, 2, 3, 4),
        CANONICAL,
        explicit_mapping={1: "OPEN", 2: "PENDING", 3: "CLOSED", 4: "REOPENED"},
    )
    assert all(item.status is EnumMappingStatus.CONFIRMED for item in result.mappings)
    assert translate_enum(result, 1) == "OPEN"


def test_unseen_runtime_value_is_preserved_and_rejected() -> None:
    result = map_enum_values(("OPEN", "CLOSED"), CANONICAL, observed_values=["OPEN", "BROKEN"])
    assert result.unseen_values == ("BROKEN",)
    with pytest.raises(UnknownEnumValueError, match="unseen"):
        translate_enum(result, "BROKEN")
    with pytest.raises(UnknownEnumValueError, match="unseen"):
        translate_enum(result, "NOT_DECLARED")


def test_review_required_value_cannot_be_translated_silently() -> None:
    result = map_enum_values(
        ("ACTIVE-CLAIM",),
        ("OPEN", "CLOSED"),
        external_descriptions={"ACTIVE-CLAIM": "claim lifecycle"},
        canonical_descriptions={"OPEN": "claim lifecycle", "CLOSED": "claim lifecycle"},
    )
    assert result.mappings[0].status is EnumMappingStatus.CONFLICTING
    with pytest.raises(UnapprovedEnumMappingError):
        translate_enum(result, "ACTIVE-CLAIM")


def test_candidate_alternatives_are_retained_for_conflicts() -> None:
    result = map_enum_values(
        ("STATE",),
        ("OPEN", "CLOSED"),
        external_descriptions={"STATE": "lifecycle state"},
        canonical_descriptions={"OPEN": "lifecycle state", "CLOSED": "lifecycle state"},
    )
    candidate = result.mappings[0]
    assert candidate.status is EnumMappingStatus.CONFLICTING
    assert candidate.canonical_value in {"OPEN", "CLOSED"}
    assert candidate.alternatives


def test_descriptions_can_provide_reviewable_support() -> None:
    result = map_enum_values(
        ("IN_PROGRESS",),
        ("OPEN", "CLOSED"),
        external_descriptions={"IN_PROGRESS": "claim is open and being worked"},
        canonical_descriptions={"OPEN": "claim is open", "CLOSED": "claim is closed"},
    )
    assert result.mappings[0].status is EnumMappingStatus.REVIEW_REQUIRED
    assert result.mappings[0].canonical_value == "OPEN"


def test_result_is_complete_and_round_trippable() -> None:
    result = map_enum_values(("OPN", "CLS"), ("OPEN", "CLOSED"))
    assert type(result).model_validate_json(result.model_dump_json()) == result
    assert result.candidate("OPN") == result.mappings[0]
    assert result.candidate("MISSING") is None


@pytest.mark.parametrize(
    "external,canonical",
    [([], CANONICAL), (["OPEN", "OPEN"], CANONICAL), (["OPEN"], ["OPEN", "OPEN"])],
)
def test_invalid_vocabularies_are_rejected(external: list[str], canonical: tuple[str, ...]) -> None:
    with pytest.raises(InvalidEnumVocabularyError):
        map_enum_values(external, canonical)


def test_explicit_mapping_must_use_declared_values() -> None:
    with pytest.raises(InvalidEnumVocabularyError):
        map_enum_values(("OPEN",), CANONICAL, explicit_mapping={"MISSING": "OPEN"})
    with pytest.raises(InvalidEnumVocabularyError):
        map_enum_values(("OPEN",), CANONICAL, explicit_mapping={"OPEN": "INVALID"})


def test_result_models_reject_incoherent_unknown_candidate() -> None:
    from crosswalk_enum_mapping import EnumValueCandidate

    with pytest.raises(ValidationError):
        EnumValueCandidate(
            external_value="BROKEN",
            canonical_value="OPEN",
            score=0,
            status=EnumMappingStatus.UNKNOWN,
        )


def test_integer_and_string_runtime_forms_share_declared_value() -> None:
    result = map_enum_values((1,), ("1",), explicit_mapping={1: "1"})
    assert translate_enum(result, "1") == "1"
    assert translate_enum(result, 1) == "1"
