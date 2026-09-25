"""Ground-truth correctness test (Phase 1c exit criterion).

PLANNER §14 requires "known machine-readable correct mapping for all three"
mock APIs. This test *proves* that claim: for each difficulty it loads the
hidden ``ground_truth.json`` and the corresponding sample payload, applies the
documented transforms generically, and asserts the result is a **valid
canonical ``Claim`` that equals the claim reconstructed from the seed data**.

Why this matters
-----------------
* It verifies the ground truth is genuinely correct and complete — not just a
  plausible-looking JSON file. If a mapping, enum, or date format were wrong,
  the produced ``Claim`` would fail validation or mismatch the seed.
* The applier here is a *verification harness*, deliberately dumb and generic.
  It is NOT Crosswalk's real mapper (which is inferred in later phases); it
  only knows how to execute an already-correct mapping spec. This keeps the
  ground truth honest without leaking it into any inference path (CHECKER §10).

The applier supports exactly the transform vocabulary used by the fixtures:
``identity``, ``parse_date:<fmt>``, ``enum:<map-name>``, and ``decimal``; and
the path syntax used by the fixtures: dotted paths, a leading ``$``, and a
single equality array filter ``[?(@.key==value)]``.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from crosswalk_mock_apis.seed_data import SEED_CLAIMS, SeedClaim

from crosswalk_canonical import Claim, ClaimStatus, Financials, Person, Policy

_FILTER_RE = re.compile(r"^\[\?\(@\.(?P<key>\w+)==(?P<value>[^)]+)\)\]$")


# --------------------------------------------------------------------------- #
# Generic path resolution over a JSON-like payload
# --------------------------------------------------------------------------- #
def _coerce_scalar(raw: str) -> str | int:
    """Interpret a filter literal: quoted -> str, bare int -> int."""
    raw = raw.strip()
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
    if raw.isdigit():
        return int(raw)
    return raw


def _split_path(external_path: str) -> list[str]:
    """Split a path on '.' but NOT on dots inside filter brackets.

    e.g. ``case.involved[?(@.roleType==1)].given`` ->
    ``["case", "involved[?(@.roleType==1)]", "given"]``.
    """
    segments: list[str] = []
    buf: list[str] = []
    depth = 0
    for char in external_path.lstrip("$").lstrip("."):
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
        if char == "." and depth == 0:
            segments.append("".join(buf))
            buf = []
        else:
            buf.append(char)
    if buf:
        segments.append("".join(buf))
    return segments


def _resolve(payload: Any, external_path: str) -> Any:
    """Resolve a fixture ``external_path`` against a payload.

    Supports dotted segments, a leading ``$``, and array filters of the form
    ``partyInfo[?(@.roleCd=='CLMT')]`` selecting the first matching element.
    Returns ``None`` if any segment is missing (a real mapper must tolerate
    absent optional fields).
    """
    current: Any = payload
    for segment in _split_path(external_path):
        if current is None:
            return None
        # Segment may be "name" or "name[?(@.k==v)]".
        name, _, filter_part = segment.partition("[")
        if name:
            if not isinstance(current, dict) or name not in current:
                return None
            current = current[name]
        if filter_part:
            match = _FILTER_RE.match("[" + filter_part)
            assert match is not None, f"unsupported filter: [{filter_part}"
            key = match.group("key")
            value = _coerce_scalar(match.group("value"))
            if not isinstance(current, list):
                return None
            current = next(
                (item for item in current if item.get(key) == value),
                None,
            )
    return current


# --------------------------------------------------------------------------- #
# Transform execution
# --------------------------------------------------------------------------- #
def _apply_transform(value: Any, transform: str, gt: dict[str, Any]) -> Any:
    """Apply one documented transform to a resolved value."""
    if value is None:
        return None
    if transform == "identity":
        return value
    if transform == "decimal":
        return Decimal(str(value))
    if transform.startswith("parse_date:"):
        fmt = transform.split(":", 1)[1]
        return datetime.strptime(value, fmt).date()
    if transform.startswith("enum:"):
        map_name = transform.split(":", 1)[1]
        enum_map: dict[str, str] = gt[map_name]
        # Keys in JSON are strings, so normalize numeric codes to str.
        return enum_map[str(value)]
    raise AssertionError(f"unknown transform: {transform}")


def _set_dotted(target: dict[str, Any], dotted: str, value: Any) -> None:
    """Set ``value`` at a dotted path like ``claim.claimant.first_name``.

    The leading ``claim`` segment is dropped (it is the object we build).
    """
    parts = dotted.split(".")
    assert parts[0] == "claim", f"canonical path must start with 'claim': {dotted}"
    parts = parts[1:]
    node = target
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def _build_claim_from_ground_truth(payload: Any, gt: dict[str, Any]) -> Claim:
    """Execute a full ground-truth mapping spec to produce a canonical Claim."""
    assembled: dict[str, Any] = {}
    for mapping in gt["field_mappings"]:
        raw = _resolve(payload, mapping["external_path"])
        transformed = _apply_transform(raw, mapping["transform"], gt)
        _set_dotted(assembled, mapping["canonical_path"], transformed)

    # Assemble nested models explicitly so validation errors are localized.
    claimant = Person(**assembled["claimant"])
    insured = Person(**assembled["insured"])
    policy = Policy(**assembled["policy"])
    financials = Financials(**assembled.get("financials", {}))
    return Claim(
        claim_id=assembled["claim_id"],
        incident_date=assembled["incident_date"],
        status=ClaimStatus(assembled["status"]),
        claimant=claimant,
        insured=insured,
        policy=policy,
        financials=financials,
    )


def _claim_from_seed(seed: SeedClaim) -> Claim:
    """Build the expected canonical Claim directly from the seed facts."""
    return Claim(
        claim_id=seed.claim_id,
        incident_date=seed.incident_date,
        status=ClaimStatus(seed.status),
        claimant=Person(
            first_name=seed.claimant.first_name,
            last_name=seed.claimant.last_name,
            person_id=seed.claimant.party_id,
        ),
        insured=Person(
            first_name=seed.insured.first_name,
            last_name=seed.insured.last_name,
            person_id=seed.insured.party_id,
        ),
        policy=Policy(
            policy_number=seed.policy_number,
            effective_date=seed.policy_effective_date,
            expiration_date=seed.policy_expiration_date,
        ),
        financials=Financials(
            reserve=seed.reserve,
            payments=seed.payments,
            total_incurred=seed.total_incurred,
        ),
    )


# --------------------------------------------------------------------------- #
# The tests
# --------------------------------------------------------------------------- #
_DIFFICULTIES = ["easy", "medium", "hard"]


def _load_ground_truth(fixtures_dir: Path, difficulty: str) -> dict[str, Any]:
    path = fixtures_dir / "external_apis" / difficulty / "ground_truth.json"
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _load_payload(fixtures_dir: Path, difficulty: str, claim_id: str) -> Any:
    path = fixtures_dir / "payloads" / difficulty / f"{claim_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("difficulty", _DIFFICULTIES)
class TestGroundTruthCorrectness:
    def test_every_seed_maps_to_expected_claim(
        self, fixtures_dir: Path, difficulty: str
    ) -> None:
        """Applying the ground truth to each payload yields the seed's Claim."""
        gt = _load_ground_truth(fixtures_dir, difficulty)
        for seed in SEED_CLAIMS:
            payload = _load_payload(fixtures_dir, difficulty, seed.claim_id)
            produced = _build_claim_from_ground_truth(payload, gt)
            expected = _claim_from_seed(seed)
            assert produced == expected, f"{difficulty}/{seed.claim_id} mismatch"

    def test_ground_truth_covers_all_canonical_fields(
        self, fixtures_dir: Path, difficulty: str
    ) -> None:
        """The mapping must populate every canonical field the seed has."""
        gt = _load_ground_truth(fixtures_dir, difficulty)
        canonical_targets = {m["canonical_path"] for m in gt["field_mappings"]}
        required = {
            "claim.claim_id",
            "claim.incident_date",
            "claim.status",
            "claim.claimant.first_name",
            "claim.claimant.last_name",
            "claim.insured.first_name",
            "claim.insured.last_name",
            "claim.policy.policy_number",
            "claim.financials.total_incurred",
        }
        missing = required - canonical_targets
        assert not missing, f"{difficulty} ground truth missing: {missing}"

    def test_status_enum_values_are_canonical(
        self, fixtures_dir: Path, difficulty: str
    ) -> None:
        """Every status the enum map targets must be a real ClaimStatus."""
        gt = _load_ground_truth(fixtures_dir, difficulty)
        for canonical_status in gt["status_enum_map"].values():
            # Raises if the value is not a valid canonical status.
            ClaimStatus(canonical_status)
