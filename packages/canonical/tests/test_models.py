"""Unit tests for the canonical data model (Phase 1a).

These cover the behaviors the rest of Crosswalk depends on:
* valid construction of every model,
* rejection of invalid input (blank IDs/names, unknown fields, bad enum,
  negative money, wrong types),
* correct parsing/coercion of dates and Decimals,
* immutability (frozen models),
* round-trip JSON serialization.

We test failure paths, not just the happy path (CHECKER §12 testing gate).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from crosswalk_canonical import Claim, ClaimStatus, Financials, Person, Policy


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #
def _valid_person(**overrides: object) -> Person:
    data: dict[str, object] = {"first_name": "John", "last_name": "Smith"}
    data.update(overrides)
    return Person(**data)  # type: ignore[arg-type]


def _valid_claim(**overrides: object) -> Claim:
    data: dict[str, object] = {
        "claim_id": "C-100",
        "incident_date": date(2026, 9, 4),
        "status": ClaimStatus.OPEN,
        "claimant": _valid_person(first_name="John", last_name="Smith"),
        "insured": _valid_person(first_name="Jane", last_name="Doe"),
        "policy": Policy(policy_number="P-99122"),
        "financials": Financials(total_incurred=Decimal("14200")),
    }
    data.update(overrides)
    return Claim(**data)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ClaimStatus enum
# --------------------------------------------------------------------------- #
class TestClaimStatus:
    def test_expected_members_exist(self) -> None:
        assert {s.value for s in ClaimStatus} == {"OPEN", "PENDING", "CLOSED", "REOPENED"}

    def test_str_enum_equals_its_value(self) -> None:
        # StrEnum members compare equal to their string value.
        assert ClaimStatus.OPEN == "OPEN"

    def test_unknown_status_rejected_on_claim(self) -> None:
        with pytest.raises(ValidationError):
            _valid_claim(status="ACTIVE")


# --------------------------------------------------------------------------- #
# Person
# --------------------------------------------------------------------------- #
class TestPerson:
    def test_valid_person_without_id(self) -> None:
        p = _valid_person()
        assert p.first_name == "John"
        assert p.person_id is None

    def test_valid_person_with_id(self) -> None:
        p = _valid_person(person_id="P882")
        assert p.person_id == "P882"

    @pytest.mark.parametrize("blank", ["", "   ", "\t"])
    def test_blank_first_name_rejected(self, blank: str) -> None:
        with pytest.raises(ValidationError):
            _valid_person(first_name=blank)

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_blank_last_name_rejected(self, blank: str) -> None:
        with pytest.raises(ValidationError):
            _valid_person(last_name=blank)

    def test_whitespace_is_stripped(self) -> None:
        p = _valid_person(first_name="  John  ")
        assert p.first_name == "John"

    def test_unknown_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Person(first_name="A", last_name="B", middle_name="C")  # type: ignore[call-arg]


# --------------------------------------------------------------------------- #
# Policy
# --------------------------------------------------------------------------- #
class TestPolicy:
    def test_minimal_policy(self) -> None:
        pol = Policy(policy_number="P-1")
        assert pol.effective_date is None
        assert pol.expiration_date is None

    def test_full_policy(self) -> None:
        pol = Policy(
            policy_number="P-1",
            effective_date=date(2026, 1, 1),
            expiration_date=date(2026, 12, 31),
        )
        assert pol.effective_date == date(2026, 1, 1)

    def test_iso_date_string_is_parsed(self) -> None:
        pol = Policy(policy_number="P-1", effective_date="2026-01-01")  # type: ignore[arg-type]
        assert pol.effective_date == date(2026, 1, 1)

    def test_blank_policy_number_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Policy(policy_number="   ")


# --------------------------------------------------------------------------- #
# Financials
# --------------------------------------------------------------------------- #
class TestFinancials:
    def test_all_optional_defaults_none(self) -> None:
        f = Financials()
        assert f.reserve is None
        assert f.payments is None
        assert f.total_incurred is None

    def test_decimal_values(self) -> None:
        f = Financials(
            reserve=Decimal("100.50"),
            payments=Decimal("25.25"),
            total_incurred=Decimal("125.75"),
        )
        assert f.total_incurred == Decimal("125.75")

    def test_money_is_not_float(self) -> None:
        # Pydantic coerces int/str to Decimal; ensure we get Decimal back so no
        # binary floating-point error creeps into money.
        f = Financials(reserve=14200)  # type: ignore[arg-type]
        assert isinstance(f.reserve, Decimal)
        assert f.reserve == Decimal("14200")

    def test_negative_money_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Financials(reserve=Decimal("-1"))


# --------------------------------------------------------------------------- #
# Claim
# --------------------------------------------------------------------------- #
class TestClaim:
    def test_valid_claim(self) -> None:
        claim = _valid_claim()
        assert claim.claim_id == "C-100"
        assert claim.status is ClaimStatus.OPEN
        assert claim.incident_date == date(2026, 9, 4)
        assert claim.claimant.first_name == "John"
        assert claim.policy.policy_number == "P-99122"
        assert claim.financials.total_incurred == Decimal("14200")

    def test_financials_defaults_to_empty(self) -> None:
        claim = _valid_claim(financials=Financials())
        assert claim.financials.reserve is None

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_blank_claim_id_rejected(self, blank: str) -> None:
        with pytest.raises(ValidationError):
            _valid_claim(claim_id=blank)

    def test_missing_required_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Claim(  # type: ignore[call-arg]
                claim_id="C-1",
                incident_date=date(2026, 9, 4),
                status=ClaimStatus.OPEN,
                claimant=_valid_person(),
                insured=_valid_person(),
                # policy intentionally omitted
            )

    def test_iso_date_string_parsed(self) -> None:
        claim = _valid_claim(incident_date="2026-09-04")
        assert claim.incident_date == date(2026, 9, 4)

    def test_unknown_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            _valid_claim(external_ref="oops")

    def test_claim_is_immutable(self) -> None:
        claim = _valid_claim()
        with pytest.raises(ValidationError):
            claim.claim_id = "C-999"  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# Serialization round-trip
# --------------------------------------------------------------------------- #
class TestSerialization:
    def test_json_round_trip(self) -> None:
        claim = _valid_claim()
        dumped = claim.model_dump_json()
        restored = Claim.model_validate_json(dumped)
        assert restored == claim

    def test_status_serializes_as_string(self) -> None:
        claim = _valid_claim()
        data = claim.model_dump(mode="json")
        assert data["status"] == "OPEN"

    def test_decimal_survives_round_trip(self) -> None:
        claim = _valid_claim(financials=Financials(total_incurred=Decimal("14200.42")))
        restored = Claim.model_validate_json(claim.model_dump_json())
        assert restored.financials.total_incurred == Decimal("14200.42")
