from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_events_endpoint_accumulates_requests() -> None:
    client = TestClient(create_app())
    client.get("/health")
    client.get("/info")

    assert len(client.get("/events").json()) == 3
