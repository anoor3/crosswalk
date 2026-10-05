"""Focused lexical, type, privacy, and uncertainty checks for mapping evidence."""

from __future__ import annotations

import pytest

from crosswalk_discovery import ExternalField, FieldType
from crosswalk_mapping.models import CanonicalField
from crosswalk_mapping.signals import normalized_tokens, score_field
from crosswalk_mapping.targets import canonical_fields
from crosswalk_profiler import FieldProfile, SemanticType, profile_field


def _target(path: str) -> CanonicalField:
    return next(field for field in canonical_fields() if field.path == path)


def _source(path: str, data_type: FieldType = FieldType.STRING, **kwargs: object) -> ExternalField:
    return ExternalField.model_validate(
        {"json_path": path, "name": path.rsplit(".", 1)[-1], "data_type": data_type, **kwargs}
    )


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("claimID", {"claim", "id"}),
        ("claim_number", {"claim", "id"}),
        ("claimantGivenName", {"claimant", "first", "name"}),
        ("insuredSurname", {"insured", "last", "name"}),
        ("APIResponseID", {"api", "response", "id"}),
        ("polNum", {"policy", "id"}),
        ("partyRef", {"person", "id"}),
        ("effDt", {"effective", "date"}),
        ("expDt", {"expiration", "date"}),
        ("pdAmt", {"payment", "amount"}),
        ("rsvAmt", {"reserve", "amount"}),
        ("firstNm", {"first", "name"}),
    ],
)
def test_reusable_word_normalization(name: str, expected: set[str]) -> None:
    assert normalized_tokens(name) == expected


def test_equivalent_specific_names_and_nested_role_context() -> None:
    target = _target("claim.claimant.first_name")
    for path in ("$.claimant.firstName", "$.data[*].claimantGivenName"):
        evidence = score_field(_source(path), target)
        assert evidence.name.score == 1.0
    assert score_field(_source("$.claimID"), _target("claim.claim_id")).name.score == 1


def test_wrong_person_role_is_not_equivalent_to_same_leaf_name() -> None:
    source = _source("$.insured.firstName")
    correct = score_field(source, _target("claim.insured.first_name"))
    wrong = score_field(source, _target("claim.claimant.first_name"))
    assert correct.name.score == 1.0
    assert wrong.name.score == 0.0
    assert "roles conflict" in wrong.name.reason


def test_unscoped_person_name_remains_weaker_than_identified_role() -> None:
    source = _source("$.firstName")
    claimant = score_field(source, _target("claim.claimant.first_name"))
    insured = score_field(source, _target("claim.insured.first_name"))
    assert claimant.name.score == insured.name.score == 0.65


@pytest.mark.parametrize(
    "path", ["$.id", "$.transactionId", "$.customer.id", "$.claim.invoiceId", "$.claim.customer.id"]
)
def test_generic_or_unrelated_identifiers_are_weak(path: str) -> None:
    evidence = score_field(_source(path), _target("claim.claim_id"))
    assert evidence.name.score is not None
    assert evidence.name.score <= 0.35
    assert "does not identify its entity" in evidence.name.reason


def test_bare_identifier_uses_nearest_entity_context() -> None:
    correct = score_field(_source("$.claim.id"), _target("claim.claim_id"))
    assert correct.name.score == 1.0
    nested_unrelated = score_field(
        _source("$.claimant.customerId"), _target("claim.claimant.person_id")
    )
    assert nested_unrelated.name.score is not None
    assert nested_unrelated.name.score <= 0.35


def test_description_overlap_is_inspectable_and_missing_is_unavailable() -> None:
    target = CanonicalField(
        path="claim.claim_id",
        name="claim_id",
        data_type=FieldType.STRING,
        description="Unique identifier for the claim.",
    )
    exact = score_field(_source("$.claimId", description=target.description), target)
    missing = score_field(_source("$.claimId"), target)
    wrong = score_field(_source("$.claimId", description="Vendor contract dates"), target)
    assert exact.description.score == 1.0
    assert missing.description.score is None
    assert wrong.description.score == 0.0
    assert "shared terms" in exact.description.reason


@pytest.mark.parametrize(
    ("source_type", "target_type", "expected"),
    [
        (FieldType.STRING, FieldType.STRING, 1.0),
        (FieldType.INTEGER, FieldType.NUMBER, 1.0),
        (FieldType.NUMBER, FieldType.INTEGER, 0.0),
        (FieldType.BOOLEAN, FieldType.NUMBER, 0.0),
        (FieldType.STRING, FieldType.NUMBER, 0.0),
        (FieldType.UNKNOWN, FieldType.STRING, None),
        (FieldType.NULL, FieldType.STRING, None),
    ],
)
def test_type_compatibility_is_explicit(
    source_type: FieldType, target_type: FieldType, expected: float | None
) -> None:
    target = CanonicalField(path="target.value", name="value", data_type=target_type)
    assert score_field(_source("$.value", source_type), target).type.score == expected


def test_union_type_evidence_is_fraction_of_compatible_alternatives() -> None:
    source = _source("$.value", extra_types=(FieldType.NUMBER,))
    target = CanonicalField(path="target.value", name="value", data_type=FieldType.STRING)
    evidence = score_field(source, target)
    assert evidence.type.score == 0.5
    assert "1/2 declared types" in evidence.type.reason


@pytest.mark.parametrize("payloads", [[], [{"claimId": None}], [{"other": "missing"}]])
def test_empty_null_and_absent_samples_do_not_invent_profile_evidence(
    payloads: list[dict[str, object]],
) -> None:
    source = _source("$.claimId")
    profile = profile_field(payloads, source.json_path)
    assert score_field(source, _target("claim.claim_id"), profile).value_profile.score is None


def test_profile_patterns_support_but_do_not_prove_meaning_or_leak_samples() -> None:
    source = _source("$.claimId")
    secret = "PRIVATE-9000001"
    profile = profile_field([{"claimId": secret}], source.json_path)
    assert profile.semantic_type is SemanticType.IDENTIFIER
    evidence = score_field(source, _target("claim.claim_id"), profile)
    assert evidence.value_profile.score == 0.75
    assert "not proof" in evidence.value_profile.reason
    assert secret not in evidence.model_dump_json()


def test_currency_hint_cannot_discriminate_financial_meanings() -> None:
    source = _source("$.amount", FieldType.NUMBER)
    profile = profile_field([{"amount": 123.45}, {"amount": 987.65}], source.json_path)
    assert profile.semantic_type is SemanticType.CURRENCY
    scores = [
        score_field(source, _target(f"claim.financials.{name}"), profile).value_profile.score
        for name in ("reserve", "payments", "total_incurred")
    ]
    assert scores == [0.75, 0.75, 0.75]


def test_observed_type_conflict_produces_zero_profile_support() -> None:
    source = _source("$.incidentDate")
    profile = profile_field([{"incidentDate": True}], source.json_path)
    evidence = score_field(source, _target("claim.incident_date"), profile)
    assert evidence.value_profile.score == 0.0


def test_profiles_for_another_path_are_rejected() -> None:
    profile = profile_field([{"other": "2026-01-01"}], "$.other")
    with pytest.raises(ValueError, match="Profile path"):
        score_field(_source("$.incidentDate"), _target("claim.incident_date"), profile)


def test_fixed_weights_exclude_unavailable_evidence_from_total() -> None:
    evidence = score_field(_source("$.claimId"), _target("claim.claim_id"))
    assert evidence.name.weight == 0.45
    assert evidence.description.weight == 0.25
    assert evidence.type.weight == 0.15
    assert evidence.value_profile.weight == 0.15
    assert evidence.value_profile.score is None
    assert evidence.score == pytest.approx(1.0)


def test_aggregate_statistics_only_and_deterministic_results() -> None:
    source = _source("$.claimId")
    profile: FieldProfile = profile_field([{"claimId": "CL-1001"}], "$.claimId")
    assert score_field(source, _target("claim.claim_id"), profile) == score_field(
        source, _target("claim.claim_id"), profile
    )
