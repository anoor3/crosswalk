from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_event_records_path() -> None:
    client = TestClient(create_app())
    client.get("/info")

    assert client.get("/events").json()[0]["path"] == "/info"
