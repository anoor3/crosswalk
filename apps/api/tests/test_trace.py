from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_api_returns_generated_trace_id() -> None:
    response = TestClient(create_app()).get("/ready")

    assert response.headers["X-Trace-Id"]


def test_api_preserves_caller_trace_id() -> None:
    response = TestClient(create_app()).get("/ready", headers={"X-Trace-Id": "request-123"})

    assert response.headers["X-Trace-Id"] == "request-123"
