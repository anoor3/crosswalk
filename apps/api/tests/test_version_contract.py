from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_version_uses_service_marker() -> None:
    response = TestClient(create_app()).get("/version")

    assert response.json() == {"status": "ok", "version": "service"}
