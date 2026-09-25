"""Integration tests for the three mock external APIs (Phase 1c).

Each mock is exercised in-process through ``httpx.ASGITransport`` — no real
network, no bound port — so the tests are fast and never flaky on CI
(CHECKER §12: "external network dependencies make tests flaky").

We assert, per API:
* health endpoint,
* list endpoint returns all seed claims,
* item endpoint returns the expected shape,
* unknown id returns 404 (failure path, not just happy path),
* the wire shape actually differs (easy/medium/hard are distinct).
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest
from crosswalk_mock_apis import easy_app, hard_app, medium_app
from fastapi import FastAPI


def _client(app: FastAPI) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture
async def easy() -> AsyncIterator[httpx.AsyncClient]:
    async with _client(easy_app) as c:
        yield c


@pytest.fixture
async def medium() -> AsyncIterator[httpx.AsyncClient]:
    async with _client(medium_app) as c:
        yield c


@pytest.fixture
async def hard() -> AsyncIterator[httpx.AsyncClient]:
    async with _client(hard_app) as c:
        yield c


# --------------------------------------------------------------------------- #
# Health
# --------------------------------------------------------------------------- #
class TestHealth:
    async def test_easy_health(self, easy: httpx.AsyncClient) -> None:
        r = await easy.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    async def test_medium_health(self, medium: httpx.AsyncClient) -> None:
        r = await medium.get("/health")
        assert r.status_code == 200

    async def test_hard_health(self, hard: httpx.AsyncClient) -> None:
        r = await hard.get("/health")
        assert r.status_code == 200


# --------------------------------------------------------------------------- #
# Easy API
# --------------------------------------------------------------------------- #
class TestEasyApi:
    async def test_list_returns_all_seeds(self, easy: httpx.AsyncClient) -> None:
        r = await easy.get("/claims")
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 4
        assert {c["claimNumber"] for c in body} == {"C-100", "C-101", "C-102", "C-103"}

    async def test_get_claim_shape(self, easy: httpx.AsyncClient) -> None:
        r = await easy.get("/claims/C-100")
        assert r.status_code == 200
        body = r.json()
        assert body["claimNumber"] == "C-100"
        assert body["dateOfLoss"] == "2026-09-04"  # ISO
        assert body["status"] == "OPEN"  # string status
        assert body["claimant"]["firstName"] == "John"
        assert body["totalIncurred"] == "14200.00"  # decimal string

    async def test_unknown_claim_404(self, easy: httpx.AsyncClient) -> None:
        r = await easy.get("/claims/NOPE")
        assert r.status_code == 404


# --------------------------------------------------------------------------- #
# Medium API
# --------------------------------------------------------------------------- #
class TestMediumApi:
    async def test_list_returns_all_seeds(self, medium: httpx.AsyncClient) -> None:
        r = await medium.get("/losses")
        assert r.status_code == 200
        assert {c["lossNo"] for c in r.json()} == {"C-100", "C-101", "C-102", "C-103"}

    async def test_get_loss_shape(self, medium: httpx.AsyncClient) -> None:
        r = await medium.get("/losses/C-100")
        assert r.status_code == 200
        body = r.json()
        assert body["lossNo"] == "C-100"
        assert body["occDt"] == "09/04/26"  # US MM/DD/YY
        assert body["stateCd"] == "OPN"  # coded status
        roles = {p["roleCd"] for p in body["partyInfo"]}
        assert roles == {"CLMT", "INSD"}

    async def test_unknown_loss_404(self, medium: httpx.AsyncClient) -> None:
        r = await medium.get("/losses/NOPE")
        assert r.status_code == 404


# --------------------------------------------------------------------------- #
# Hard API
# --------------------------------------------------------------------------- #
class TestHardApi:
    async def test_list_returns_all_seeds(self, hard: httpx.AsyncClient) -> None:
        r = await hard.get("/cases")
        assert r.status_code == 200
        assert {c["case"]["ref"] for c in r.json()} == {"C-100", "C-101", "C-102", "C-103"}

    async def test_get_case_shape(self, hard: httpx.AsyncClient) -> None:
        r = await hard.get("/cases/C-100")
        assert r.status_code == 200
        case = r.json()["case"]
        assert case["ref"] == "C-100"
        assert case["incident"]["occurred_at"] == "2026/09/04"  # slashed
        assert case["state"] == 1  # numeric status
        assert case["ledger"]["inc"] == "14200.00"

    async def test_unknown_case_404(self, hard: httpx.AsyncClient) -> None:
        r = await hard.get("/cases/NOPE")
        assert r.status_code == 404


# --------------------------------------------------------------------------- #
# Cross-API: the same claim really is served in three different shapes
# --------------------------------------------------------------------------- #
class TestShapesDiffer:
    async def test_c100_top_level_keys_differ(
        self,
        easy: httpx.AsyncClient,
        medium: httpx.AsyncClient,
        hard: httpx.AsyncClient,
    ) -> None:
        e = set((await easy.get("/claims/C-100")).json().keys())
        m = set((await medium.get("/losses/C-100")).json().keys())
        h = set((await hard.get("/cases/C-100")).json().keys())
        # All three describe C-100 but with disjoint top-level vocabularies.
        assert e != m
        assert m != h
        assert e != h
        assert h == {"case"}  # hard nests everything under a single key
