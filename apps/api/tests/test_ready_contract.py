from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_ready_uses_ready_version_marker() -> None:
    response = TestClient(create_app()).get("/ready")

    assert response.json() == {"status": "ok", "version": "ready"}
