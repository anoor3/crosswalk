from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_counts_post_requests() -> None:
    client = TestClient(create_app())
    client.post("/jobs", json={"tenant_id": "t1", "kind": "discover"})

    assert client.get("/metrics").json()["requests.total"] == 2
