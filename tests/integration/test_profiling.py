"""Integration: discovery + profiler over the real mock-API fixtures (Phase 3).

Wires the two deterministic layers together end to end: `analyze_openapi`
produces field paths from a fixture's OpenAPI spec, and the profiler computes a
`FieldProfile` for each of those paths from the fixture's sample payloads. This
proves the profiler is usable on real discovered fields — the Phase 3 exit
criterion (a reusable profiler independent of any AI).

Assertions target semantic types that are *robust* given the four-claim seed:
identifiers, dates, currency, and the enum candidates that genuinely repeat
(party role codes). Fields whose sample happens to be all-distinct (e.g. a
status code across four claims with four different statuses) are intentionally
not asserted as enums — the profiler is honest about small samples, and the
test reflects that rather than forcing a convenient answer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from crosswalk_discovery import analyze_openapi
from crosswalk_profiler import FieldProfile, SemanticType, profile_fields

# (difficulty, item endpoint) per fixture.
_ITEM_ENDPOINTS = {
    "easy": "/claims/{claim_number}",
    "medium": "/losses/{loss_no}",
    "hard": "/cases/{ref}",
}


def _profiles(fixtures_dir: Path, difficulty: str) -> dict[str, FieldProfile]:
    spec: dict[str, Any] = json.loads(
        (fixtures_dir / "schemas" / difficulty / "openapi.json").read_text()
    )
    catalog = analyze_openapi(spec)
    endpoint = catalog.endpoint("GET", _ITEM_ENDPOINTS[difficulty])
    assert endpoint is not None
    leaf_paths = [
        f.json_path
        for f in endpoint.response_fields
        if f.data_type.value not in ("object", "array")
    ]
    payloads: list[Any] = json.loads(
        (fixtures_dir / "payloads" / difficulty / "claims.json").read_text()
    )
    return profile_fields(payloads, leaf_paths)


class TestEasyProfiling:
    def test_identifier_and_date_and_currency(self, fixtures_dir: Path) -> None:
        profs = _profiles(fixtures_dir, "easy")
        assert profs["$.claimNumber"].semantic_type is SemanticType.IDENTIFIER
        assert profs["$.dateOfLoss"].semantic_type is SemanticType.DATE
        assert profs["$.dateOfLoss"].detected_date_format == "%Y-%m-%d"
        assert profs["$.totalIncurred"].semantic_type is SemanticType.CURRENCY

    def test_no_nulls_in_required_id(self, fixtures_dir: Path) -> None:
        profs = _profiles(fixtures_dir, "easy")
        assert profs["$.claimNumber"].null_rate == 0.0
        assert profs["$.claimNumber"].unique_rate == 1.0


class TestMediumProfiling:
    def test_abbreviated_identifier_and_us_date(self, fixtures_dir: Path) -> None:
        profs = _profiles(fixtures_dir, "medium")
        assert profs["$.lossNo"].semantic_type is SemanticType.IDENTIFIER
        assert profs["$.occDt"].semantic_type is SemanticType.DATE
        assert profs["$.occDt"].detected_date_format == "%m/%d/%y"

    def test_party_role_code_is_enum_candidate(self, fixtures_dir: Path) -> None:
        # roleCd repeats (CLMT/INSD across two parties per claim) -> low
        # cardinality across 8 observations.
        profs = _profiles(fixtures_dir, "medium")
        role = profs["$.partyInfo[*].roleCd"]
        assert role.semantic_type is SemanticType.ENUM_CANDIDATE
        assert role.sample_count == 8
        assert role.unique_count == 2

    def test_fractional_money_is_currency(self, fixtures_dir: Path) -> None:
        profs = _profiles(fixtures_dir, "medium")
        assert profs["$.incurredAmt"].semantic_type is SemanticType.CURRENCY


class TestHardProfiling:
    def test_nested_identifier_date_currency(self, fixtures_dir: Path) -> None:
        profs = _profiles(fixtures_dir, "hard")
        assert profs["$.case.ref"].semantic_type is SemanticType.IDENTIFIER
        assert profs["$.case.incident.occurred_at"].semantic_type is SemanticType.DATE
        assert profs["$.case.incident.occurred_at"].detected_date_format == "%Y/%m/%d"
        assert profs["$.case.ledger.inc"].semantic_type is SemanticType.CURRENCY

    def test_numeric_role_type_is_enum_candidate(self, fixtures_dir: Path) -> None:
        profs = _profiles(fixtures_dir, "hard")
        role = profs["$.case.involved[*].roleType"]
        assert role.semantic_type is SemanticType.ENUM_CANDIDATE
        assert role.unique_count == 2


class TestReusabilityAndSafety:
    @pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
    def test_all_fields_profiled_without_error(
        self, fixtures_dir: Path, difficulty: str
    ) -> None:
        # Every discovered leaf field yields a profile with consistent counts —
        # the profiler tolerates every real shape, including fan-out fields.
        profs = _profiles(fixtures_dir, difficulty)
        assert profs
        for prof in profs.values():
            assert prof.sample_count >= prof.present_count
            assert prof.present_count >= prof.null_count
            assert 0.0 <= prof.null_rate <= 1.0
            assert len(prof.sample_values) <= 10  # capped (CHECKER §15 privacy)

    def test_profiler_needs_no_ai(self, fixtures_dir: Path) -> None:
        # Sanity: profiling is pure computation over payloads — importing and
        # running it requires nothing beyond discovery + the payloads.
        profs = _profiles(fixtures_dir, "easy")
        assert isinstance(next(iter(profs.values())), FieldProfile)
