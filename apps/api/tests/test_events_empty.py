from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_events_returns_request_event_for_itself() -> None:
    response = TestClient(create_app()).get("/events")

    assert response.json()[0]["path"] == "/events"
