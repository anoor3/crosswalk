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


def test_configured_open_state(tmp_path: Path) -> None:
    with TestClient(
        create_app(settings=ApiSettings(review_database=str(tmp_path / "r.db")))
    ) as client:
        client.post("/reviews", json={"tenant_id": "t", "review_id": "r", "candidate": candidate()})
        assert client.get("/reviews", params={"tenant_id": "t", "state": "OPEN"}).json()["items"]
