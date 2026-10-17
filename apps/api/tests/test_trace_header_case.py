from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_trace_header_accepts_lowercase_input() -> None:
    response = TestClient(create_app()).get("/ready", headers={"x-trace-id": "abc"})

    assert response.headers["X-Trace-Id"] == "abc"
