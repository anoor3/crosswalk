from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_ready_trace_is_preserved() -> None:
    response = TestClient(create_app()).get("/ready", headers={"X-Trace-Id": "ready-1"})

    assert response.headers["X-Trace-Id"] == "ready-1"
