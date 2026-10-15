"""Discovery → profiler-path relationship checks over real fixture payloads."""

import json
from pathlib import Path

from crosswalk_relationships import (
    FieldReference,
    RelationshipStatus,
    discover_relationship,
)


def _payloads(fixtures_dir: Path, api: str) -> list[object]:
    return json.loads((fixtures_dir / "payloads" / api / "claims.json").read_text())


def test_party_ids_overlap_across_real_api_shapes(fixtures_dir: Path) -> None:
    source = FieldReference(
        endpoint="easy.claims",
        json_path="$.claimant.partyId",
        name="partyId",
        data_type="string",
    )
    target = FieldReference(
        endpoint="hard.cases",
        json_path="$.case.involved[*].id",
        name="id",
        data_type="string",
    )
    candidate = discover_relationship(
        source,
        target,
        _payloads(fixtures_dir, "easy"),
        _payloads(fixtures_dir, "hard"),
    )
    assert candidate.evidence is not None
    assert candidate.evidence.overlap_count == 4
    assert candidate.status in (
        RelationshipStatus.HIGH_CONFIDENCE,
        RelationshipStatus.REVIEW_REQUIRED,
    )
    assert candidate.target == target


def test_medium_party_references_overlap_hard_party_ids(fixtures_dir: Path) -> None:
    source = FieldReference(
        endpoint="medium.losses",
        json_path="$.partyInfo[*].partyRef",
        name="partyRef",
        data_type="string",
    )
    target = FieldReference(
        endpoint="hard.cases",
        json_path="$.case.involved[*].id",
        name="id",
        data_type="string",
    )
    candidate = discover_relationship(
        source,
        target,
        _payloads(fixtures_dir, "medium"),
        _payloads(fixtures_dir, "hard"),
    )
    assert candidate.evidence is not None
    assert candidate.evidence.overlap_rate == 1.0


def test_unrelated_fields_remain_unresolved(fixtures_dir: Path) -> None:
    source = FieldReference(endpoint="easy.claims", json_path="$.claimNumber", name="claimNumber")
    target = FieldReference(endpoint="hard.cases", json_path="$.case.involved[*].id", name="id")
    candidate = discover_relationship(
        source,
        target,
        _payloads(fixtures_dir, "easy"),
        _payloads(fixtures_dir, "hard"),
    )
    assert candidate.status is RelationshipStatus.UNRESOLVED
    assert candidate.target is None
