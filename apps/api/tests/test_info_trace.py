from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_info_propagates_trace_id() -> None:
    response = TestClient(create_app()).get("/info", headers={"X-Trace-Id": "info-1"})

    assert response.headers["X-Trace-Id"] == "info-1"
