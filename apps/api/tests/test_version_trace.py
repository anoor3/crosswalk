from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_version_trace_is_preserved() -> None:
    response = TestClient(create_app()).get("/version", headers={"X-Trace-Id": "v1"})

    assert response.headers["X-Trace-Id"] == "v1"
