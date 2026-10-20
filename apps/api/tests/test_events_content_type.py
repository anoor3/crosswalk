from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_events_endpoint_is_json() -> None:
    response = TestClient(create_app()).get("/events")

    assert response.headers["content-type"].startswith("application/json")
