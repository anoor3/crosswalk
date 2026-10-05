"""Discovery → profiler → mapper without importing benchmark answers."""

import json
from pathlib import Path

import pytest

from crosswalk_discovery import analyze_openapi
from crosswalk_mapping import MappingCandidate, MappingStatus, map_fields
from crosswalk_profiler import profile_fields


@pytest.mark.parametrize(
    ("api", "endpoint_path"),
    [
        ("easy", "/claims/{claim_number}"),
        ("medium", "/losses/{loss_no}"),
        ("hard", "/cases/{ref}"),
    ],
)
def test_complete_pipeline(fixtures_dir: Path, api: str, endpoint_path: str) -> None:
    spec = json.loads((fixtures_dir / "schemas" / api / "openapi.json").read_text())
    samples = json.loads((fixtures_dir / "payloads" / api / "claims.json").read_text())
    endpoint = analyze_openapi(spec).endpoint("GET", endpoint_path)
    assert endpoint is not None
    fields = endpoint.response_fields
    profiles = profile_fields(samples, [field.json_path for field in fields])
    candidates = map_fields(fields, profiles)
    assert candidates == map_fields(fields, profiles)
    assert [item.external_path for item in candidates] == [field.json_path for field in fields]
    assert all(
        item.status not in (MappingStatus.CONFIRMED, MappingStatus.REJECTED) for item in candidates
    )
    for item in candidates:
        assert MappingCandidate.model_validate_json(item.model_dump_json()) == item
        if item.evidence is not None:
            assert item.score == item.evidence.score
        if "[*]" in item.external_path:
            assert item.status != MappingStatus.HIGH_CONFIDENCE
        if item.canonical_path and ".financials." in item.canonical_path:
            assert item.status in (MappingStatus.REVIEW_REQUIRED, MappingStatus.CONFLICTING)
