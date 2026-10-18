from crosswalk_api import create_app
from crosswalk_api.request_limits import MAX_REQUEST_BYTES
from fastapi.testclient import TestClient


def test_request_at_limit_is_accepted() -> None:
    response = TestClient(create_app()).get(
        "/ready", headers={"Content-Length": str(MAX_REQUEST_BYTES)}
    )

    assert response.status_code == 200
