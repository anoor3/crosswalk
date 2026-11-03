from fastapi.testclient import TestClient

from crosswalk_api import create_app


def test_list_reviews_returns_open_reviews_for_tenant() -> None:
    client = TestClient(create_app())
    payload = {
        "tenant_id": "tenant-a",
        "review_id": "review-1",
        "candidate": {
            "external_path": "$.id",
            "canonical_path": None,
            "score": 0,
            "status": "UNRESOLVED",
            "evidence": None,
        },
    }
    client.post("/reviews", json=payload)
    payload["tenant_id"] = "tenant-b"
    payload["review_id"] = "review-2"
    client.post("/reviews", json=payload)

    response = client.get("/reviews", params={"tenant_id": "tenant-a"})

    assert [item["review_id"] for item in response.json()["items"]] == ["review-1"]
