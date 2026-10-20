from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_events_subroute_is_not_found() -> None:
    assert TestClient(create_app()).get("/events/detail").status_code == 404
