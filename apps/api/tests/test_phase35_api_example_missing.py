from fastapi.testclient import TestClient
from crosswalk_api import create_app


def candidate() -> dict[str, object]:
    return {"external_path": "$.id", "canonical_path": None, "score": 0, "status": "UNRESOLVED", "evidence": None}


def open_review(client: TestClient, review_id: str = "r1", tenant_id: str = "t1") -> None:
    client.post("/reviews", json={"tenant_id": tenant_id, "review_id": review_id, "candidate": candidate()})

def test_review_example_missing_returns_404() -> None:
    assert TestClient(create_app()).get("/reviews/missing/example", params={"tenant_id":"t1"}).status_code == 404
