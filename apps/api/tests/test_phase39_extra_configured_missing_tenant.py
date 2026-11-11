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


def test_configured_missing_tenant(tmp_path: Path) -> None:
    with TestClient(
        create_app(settings=ApiSettings(review_database=str(tmp_path / "r.db")))
    ) as client:
        assert client.get("/reviews/r", params={"tenant_id": "other"}).status_code == 404
