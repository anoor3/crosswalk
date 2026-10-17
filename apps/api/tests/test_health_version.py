from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_health_uses_configured_version() -> None:
    response = TestClient(create_app(version="2.0.0")).get("/health")

    assert response.json()["version"] == "2.0.0"
