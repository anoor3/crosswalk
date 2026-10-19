from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_counts_not_found_requests() -> None:
    client = TestClient(create_app())
    client.get("/missing")

    assert client.get("/metrics").json()["requests.total"] == 2
