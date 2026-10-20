from crosswalk_api import EventLog, create_app
from fastapi.testclient import TestClient


def test_app_event_log_is_independent_of_trace_header() -> None:
    events = EventLog()
    TestClient(create_app(events=events)).get("/health", headers={"X-Trace-Id": "t1"})

    assert events.snapshot()[0]["event"] == "request.received"
