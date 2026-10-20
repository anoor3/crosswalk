from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_events_returns_ok() -> None:
    assert TestClient(create_app()).get("/events").status_code == 200
