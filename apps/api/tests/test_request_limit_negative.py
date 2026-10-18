from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_negative_length_request_is_not_rejected_as_oversized() -> None:
    response = TestClient(create_app()).get("/ready", headers={"Content-Length": "-1"})

    assert response.status_code == 200
