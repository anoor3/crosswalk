from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_events_endpoint_rejects_post() -> None:
    assert TestClient(create_app()).post("/events").status_code == 405
