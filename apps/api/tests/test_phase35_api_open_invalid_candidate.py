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


def test_review_open_invalid_candidate_returns_422() -> None:
    response = TestClient(create_app()).post(
        "/reviews",
        json={
            "tenant_id": "t1",
            "review_id": "r1",
            "candidate": {
                "external_path": "$.id",
                "status": "BAD",
                "score": 0,
                "canonical_path": None,
                "evidence": None,
            },
        },
    )
    assert response.status_code == 422
