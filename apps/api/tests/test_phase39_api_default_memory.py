from crosswalk_api import create_app
from fastapi.testclient import TestClient


def candidate() -> dict[str, object]:
    return {
        "external_path": "$.id",
        "canonical_path": None,
        "score": 0,
        "status": "UNRESOLVED",
        "evidence": None,
    }


def test_default_memory_is_available() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/reviews/summary", params={"tenant_id": "t"}).status_code == 200
