from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_events_endpoint_has_trace_id() -> None:
    response = TestClient(create_app()).get("/events", headers={"X-Trace-Id": "e1"})

    assert response.headers["X-Trace-Id"] == "e1"
