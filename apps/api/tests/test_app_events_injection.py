from crosswalk_api import EventLog, create_app
from fastapi.testclient import TestClient


def test_app_uses_injected_event_log() -> None:
    events = EventLog()
    TestClient(create_app(events=events)).get("/health")

    assert events.snapshot()[0]["path"] == "/health"
