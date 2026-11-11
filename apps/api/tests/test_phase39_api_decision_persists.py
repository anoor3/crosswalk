from pathlib import Path

from crosswalk_api import create_app
from crosswalk_api.settings import ApiSettings
from fastapi.testclient import TestClient


def candidate() -> dict[str, object]:
    return {
        "external_path": "$.id",
        "canonical_path": None,
        "score": 0,
        "status": "UNRESOLVED",
        "evidence": None,
    }


def test_decision_persists(tmp_path: Path) -> None:
    path = tmp_path / "r.db"
    with TestClient(create_app(settings=ApiSettings(review_database=str(path)))) as client:
        client.post("/reviews", json={"tenant_id": "t", "review_id": "r", "candidate": candidate()})
        assert (
            client.post(
                "/reviews/r/decision",
                json={
                    "tenant_id": "t",
                    "action": "REJECT",
                    "reviewer_id": "a",
                    "expected_version": 0,
                    "rationale": "no",
                },
            ).status_code
            == 200
        )
    with TestClient(create_app(settings=ApiSettings(review_database=str(path)))) as client:
        assert client.get("/reviews/r", params={"tenant_id": "t"}).json()["state"] == "REJECTED"
