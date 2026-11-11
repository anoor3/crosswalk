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


def test_open_persists(tmp_path: Path) -> None:
    path = tmp_path / "r.db"
    with TestClient(create_app(settings=ApiSettings(review_database=str(path)))) as client:
        assert (
            client.post(
                "/reviews", json={"tenant_id": "t", "review_id": "r", "candidate": candidate()}
            ).status_code
            == 201
        )
    with TestClient(create_app(settings=ApiSettings(review_database=str(path)))) as client:
        assert client.get("/reviews/r", params={"tenant_id": "t"}).status_code == 200
