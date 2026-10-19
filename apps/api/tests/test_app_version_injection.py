from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_app_uses_injected_version() -> None:
    response = TestClient(create_app(version="9.9.9")).get("/health")

    assert response.json()["version"] == "9.9.9"
