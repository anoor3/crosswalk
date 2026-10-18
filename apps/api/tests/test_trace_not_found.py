from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_trace_header_applies_to_not_found() -> None:
    response = TestClient(create_app()).get("/missing", headers={"X-Trace-Id": "missing-1"})

    assert response.headers["X-Trace-Id"] == "missing-1"
