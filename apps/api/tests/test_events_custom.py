from crosswalk_api import EventLog, create_app
from fastapi.testclient import TestClient


def test_events_endpoint_includes_custom_event() -> None:
    events = EventLog()
    events.record("startup", {"source": "test"})

    response = TestClient(create_app(events=events)).get("/events")

    assert any(event["event"] == "startup" for event in response.json())
