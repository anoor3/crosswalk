from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_events_endpoint_enforces_request_limit() -> None:
    response = TestClient(create_app()).get("/events", headers={"Content-Length": "2000000"})

    assert response.status_code == 413
