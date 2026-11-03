from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_open_review_has_no_evaluation_example() -> None:
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

    response = client.get("/reviews/review-1/example", params={"tenant_id": "tenant-a"})

    assert response.status_code == 409
