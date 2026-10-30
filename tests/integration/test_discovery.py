"""Integration tests: analyze_openapi over the real mock-API OpenAPI specs.

These run the full discovery pipeline against the exact OpenAPI documents the
mock APIs emit (fixtures/schemas/{easy,medium,hard}/openapi.json), proving the
parser works on real generated specs — not just synthetic snippets
(CHECKER §14: "parser only works on project fixtures" is a failure; here we
also add synthetic edge cases in test_analyzer_edge.py).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from crosswalk_discovery import ApiCatalog, analyze_openapi


def _load(fixtures_dir: Path, difficulty: str) -> dict[str, Any]:
    path = fixtures_dir / "schemas" / difficulty / "openapi.json"
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _catalog(fixtures_dir: Path, difficulty: str) -> ApiCatalog:
    return analyze_openapi(_load(fixtures_dir, difficulty))


def _paths(catalog: ApiCatalog) -> set[str]:
    return {e.path for e in catalog.endpoints}


def _field_paths(catalog: ApiCatalog, method: str, path: str) -> set[str]:
    endpoint = catalog.endpoint(method, path)
    assert endpoint is not None
    return {f.json_path for f in endpoint.response_fields}


class TestEasyFixture:
    def test_info_and_endpoints(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "easy")
        assert cat.title == "Acme Claims API (easy)"
        assert cat.openapi_version == "3.1.0"
        assert _paths(cat) == {"/health", "/claims", "/claims/{claim_number}"}

    def test_nested_ref_flattened(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "easy")
        paths = _field_paths(cat, "GET", "/claims/{claim_number}")
        # EasyParty $ref resolved and nested under claimant/insured.
        assert "$.claimant.firstName" in paths
        assert "$.insured.partyId" in paths

    def test_money_is_nullable(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "easy")
        endpoint = cat.endpoint("GET", "/claims/{claim_number}")
        assert endpoint is not None
        by = {f.json_path: f for f in endpoint.response_fields}
        assert by["$.totalIncurred"].nullable is True
        assert by["$.claimNumber"].nullable is False
        assert by["$.claimNumber"].required is True

    def test_list_is_collection(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "easy")
        list_ep = cat.endpoint("GET", "/claims")
        item_ep = cat.endpoint("GET", "/claims/{claim_number}")
        assert list_ep is not None and item_ep is not None
        assert list_ep.response_is_collection is True
        assert item_ep.response_is_collection is False

    def test_path_parameter_detected(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "easy")
        endpoint = cat.endpoint("GET", "/claims/{claim_number}")
        assert endpoint is not None
        params = {p.name: p for p in endpoint.parameters}
        assert params["claim_number"].location == "path"
        assert params["claim_number"].required is True


class TestMediumFixture:
    def test_array_of_objects_paths(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "medium")
        paths = _field_paths(cat, "GET", "/losses/{loss_no}")
        assert "$.partyInfo[*].firstNm" in paths
        assert "$.partyInfo[*].roleCd" in paths

    def test_array_items_flagged(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "medium")
        endpoint = cat.endpoint("GET", "/losses/{loss_no}")
        assert endpoint is not None
        by = {f.json_path: f for f in endpoint.response_fields}
        assert by["$.partyInfo[*].firstNm"].is_array_item is True
        assert by["$.lossNo"].is_array_item is False


class TestHardFixture:
    def test_deep_nested_paths(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "hard")
        paths = _field_paths(cat, "GET", "/cases/{ref}")
        assert "$.case.involved[*].given" in paths
        assert "$.case.incident.occurred_at" in paths
        assert "$.case.ledger.inc" in paths

    def test_numeric_status_is_integer(self, fixtures_dir: Path) -> None:
        cat = _catalog(fixtures_dir, "hard")
        endpoint = cat.endpoint("GET", "/cases/{ref}")
        assert endpoint is not None
        by = {f.json_path: f for f in endpoint.response_fields}
        assert by["$.case.state"].data_type.value == "integer"


class TestUnsupportedIsMinimalAndExplicit:
    @pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
    def test_only_health_additional_properties(
        self, fixtures_dir: Path, difficulty: str
    ) -> None:
        cat = _catalog(fixtures_dir, difficulty)
        # The only thing the parser can't fully model in these specs is the
        # /health dynamic-map response — and it is recorded explicitly.
        assert len(cat.unsupported) == 1
        only = cat.unsupported[0]
        assert only.construct_type == "additionalProperties (open map)"
        assert "/health" in only.location
