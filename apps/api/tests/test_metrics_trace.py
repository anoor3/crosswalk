from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_metrics_propagates_trace_id() -> None:
    response = TestClient(create_app()).get("/metrics", headers={"X-Trace-Id": "m1"})

    assert response.headers["X-Trace-Id"] == "m1"
