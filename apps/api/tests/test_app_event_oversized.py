from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_records_oversized_path() -> None:
    client = TestClient(create_app())
    response = client.get("/events", headers={"Content-Length": "2000000"})

    assert response.status_code == 413
