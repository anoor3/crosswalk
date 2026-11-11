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


def test_database_summary_empty(tmp_path: Path) -> None:
    with TestClient(
        create_app(settings=ApiSettings(review_database=str(tmp_path / "r.db")))
    ) as client:
        assert client.get("/reviews/summary", params={"tenant_id": "t"}).json()["total"] == 0
