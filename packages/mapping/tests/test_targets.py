"""The target catalog tracks the canonical contract rather than fixture labels."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from crosswalk_canonical import Claim, ClaimStatus, Financials, Person, Policy
from crosswalk_discovery import FieldType
from crosswalk_mapping.targets import canonical_fields
from crosswalk_profiler import SemanticType


def test_all_canonical_scalar_leaves_and_no_container_targets() -> None:
    expected = {f"claim.{name}" for name in ("claim_id", "incident_date", "status")}
    for prefix, model in (
        ("claimant", Person),
        ("insured", Person),
        ("policy", Policy),
        ("financials", Financials),
    ):
        expected.update(f"claim.{prefix}.{name}" for name in model.model_fields)
    assert {field.path for field in canonical_fields()} == expected
    assert len(canonical_fields()) == 15


def test_targets_preserve_types_nullability_and_enum_vocabulary() -> None:
    fields = {field.path: field for field in canonical_fields()}
    incident = fields["claim.incident_date"]
    assert Claim.model_fields["incident_date"].annotation is date
    assert incident.data_type is FieldType.STRING
    assert incident.semantic_type is SemanticType.DATE
    assert not incident.nullable
    reserve = fields["claim.financials.reserve"]
    assert Financials.model_fields["reserve"].annotation == Decimal | None
    assert reserve.data_type is FieldType.NUMBER
    assert reserve.semantic_type is SemanticType.CURRENCY
    assert reserve.nullable
    assert fields["claim.claim_id"].semantic_type is SemanticType.IDENTIFIER
    assert fields["claim.claimant.person_id"].nullable
    assert fields["claim.status"].enum_values == tuple(member.value for member in ClaimStatus)


def test_person_role_context_is_preserved_from_canonical_descriptions() -> None:
    fields = {field.path: field for field in canonical_fields()}
    claimant = fields["claim.claimant.first_name"]
    insured = fields["claim.insured.first_name"]
    for canonical, target in (
        (Claim.model_fields["claimant"], claimant),
        (Claim.model_fields["insured"], insured),
        (Person.model_fields["first_name"], claimant),
    ):
        assert canonical.description is not None
        assert canonical.description in target.description
    assert claimant.description != insured.description


def test_catalog_is_deterministic_and_immutable() -> None:
    first = canonical_fields()
    assert first == canonical_fields()
    with pytest.raises(ValidationError):
        first[0].path = "changed"
