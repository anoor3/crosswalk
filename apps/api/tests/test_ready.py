from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_ready_endpoint_is_available() -> None:
    response = TestClient(create_app()).get("/ready")
    assert response.json()["status"] == "ok"
