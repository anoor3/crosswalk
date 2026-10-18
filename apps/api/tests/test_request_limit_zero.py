from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_zero_length_request_is_accepted() -> None:
    response = TestClient(create_app()).get("/ready", headers={"Content-Length": "0"})

    assert response.status_code == 200
