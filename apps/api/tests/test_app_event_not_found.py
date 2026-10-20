from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_records_not_found_path() -> None:
    client = TestClient(create_app())
    client.get("/missing")

    assert client.get("/events").json()[0]["path"] == "/missing"
