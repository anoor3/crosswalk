from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_counts_multiple_requests() -> None:
    client = TestClient(create_app())
    client.get("/health")
    client.get("/info")

    assert client.get("/metrics").json()["requests.total"] == 3
