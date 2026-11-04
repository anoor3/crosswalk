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


def open_review(client: TestClient, review_id: str = "r1", tenant_id: str = "t1") -> None:
    client.post(
        "/reviews", json={"tenant_id": tenant_id, "review_id": review_id, "candidate": candidate()}
    )


def test_review_list_empty_tenant() -> None:
    response = TestClient(create_app()).get("/reviews", params={"tenant_id": "none"})
    assert response.json()["items"] == []
