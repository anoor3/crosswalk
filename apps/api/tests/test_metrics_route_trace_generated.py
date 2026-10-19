from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_metrics_generates_trace_when_missing() -> None:
    response = TestClient(create_app()).get("/metrics")

    assert response.headers["X-Trace-Id"]
