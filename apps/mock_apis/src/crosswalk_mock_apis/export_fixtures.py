"""Generate sample payloads and OpenAPI specs for the mock APIs.

Run with::

    uv run python -m crosswalk_mock_apis.export_fixtures

This writes, for each difficulty:
* ``fixtures/payloads/<difficulty>/claims.json``      — the full list response
* ``fixtures/payloads/<difficulty>/<id>.json``        — one per seed claim
* ``fixtures/schemas/<difficulty>/openapi.json``       — the generated OpenAPI

Everything is derived deterministically from the seed data and the apps, so
re-running never produces spurious diffs. This is tooling, not part of any
served app, and it does NOT touch the hidden ground truth.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from .easy import create_app as create_easy_app
from .hard import create_app as create_hard_app
from .medium import create_app as create_medium_app
from .seed_data import SEED_CLAIMS

# fixtures/ lives at the repo root: apps/mock_apis/src/crosswalk_mock_apis/ -> up 4.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_FIXTURES = _REPO_ROOT / "fixtures"

# Per-difficulty: (app factory, list endpoint, item endpoint template).
_APIS: dict[str, tuple[FastAPI, str, str]] = {
    "easy": (create_easy_app(), "/claims", "/claims/{id}"),
    "medium": (create_medium_app(), "/losses", "/losses/{id}"),
    "hard": (create_hard_app(), "/cases", "/cases/{id}"),
}


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def export() -> None:
    """Export payloads and OpenAPI specs for all three APIs."""
    for difficulty, (app, list_path, item_tmpl) in _APIS.items():
        client = TestClient(app)

        # Full list response.
        list_resp = client.get(list_path)
        list_resp.raise_for_status()
        _write_json(_FIXTURES / "payloads" / difficulty / "claims.json", list_resp.json())

        # One payload per seed claim.
        for seed in SEED_CLAIMS:
            item_resp = client.get(item_tmpl.format(id=seed.claim_id))
            item_resp.raise_for_status()
            _write_json(
                _FIXTURES / "payloads" / difficulty / f"{seed.claim_id}.json",
                item_resp.json(),
            )

        # OpenAPI spec (FastAPI-generated).
        _write_json(_FIXTURES / "schemas" / difficulty / "openapi.json", app.openapi())

        print(f"exported {difficulty}: {len(SEED_CLAIMS)} payloads + openapi")


if __name__ == "__main__":
    export()
