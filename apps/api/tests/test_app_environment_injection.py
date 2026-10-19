from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_uses_injected_environment() -> None:
    response = TestClient(create_app(environment="staging")).get("/info")

    assert response.json()["environment"] == "staging"
