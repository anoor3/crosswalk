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


def test_open_review_route_returns_open_record() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/reviews",
        json={"tenant_id": "tenant-a", "review_id": "review-1", "candidate": candidate()},
    )

    assert response.status_code == 201
    assert response.json()["state"] == "OPEN"
    assert response.json()["version"] == 0
