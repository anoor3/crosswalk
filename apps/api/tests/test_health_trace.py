from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_health_trace_is_preserved() -> None:
    response = TestClient(create_app()).get("/health", headers={"X-Trace-Id": "health-1"})

    assert response.headers["X-Trace-Id"] == "health-1"
