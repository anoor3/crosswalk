from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_health_remains_ok_in_configured_environment() -> None:
    response = TestClient(create_app(environment="production")).get("/health")

    assert response.json()["status"] == "ok"
