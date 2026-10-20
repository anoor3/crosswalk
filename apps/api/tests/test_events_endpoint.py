from crosswalk_api import EventLog, create_app
from fastapi.testclient import TestClient


def test_events_endpoint_reports_requests() -> None:
    events = EventLog()
    client = TestClient(create_app(events=events))
    client.get("/health")

    response = client.get("/events")

    assert response.json()[0]["event"] == "request.received"
