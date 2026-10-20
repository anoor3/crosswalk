from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_event_count_matches_requests() -> None:
    client = TestClient(create_app())
    client.get("/health")
    client.get("/info")

    assert len(client.get("/events").json()) == 3
