from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_api_rejects_malformed_content_length() -> None:
    response = TestClient(create_app()).get("/ready", headers={"Content-Length": "invalid"})

    assert response.status_code == 413
