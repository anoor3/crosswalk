from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_get_review_route_reads_open_record() -> None:
    client = TestClient(create_app())
    client.post(
        "/reviews",
        json={
            "tenant_id": "tenant-a",
            "review_id": "review-1",
            "candidate": {
                "external_path": "$.id",
                "canonical_path": None,
                "score": 0,
                "status": "UNRESOLVED",
                "evidence": None,
            },
        },
    )

    response = client.get("/reviews/review-1", params={"tenant_id": "tenant-a"})

    assert response.status_code == 200
    assert response.json()["review_id"] == "review-1"
