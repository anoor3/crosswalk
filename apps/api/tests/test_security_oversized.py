from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_security_headers_apply_to_oversized_request() -> None:
    response = TestClient(create_app()).get("/ready", headers={"Content-Length": "2000000"})

    assert response.headers["X-Content-Type-Options"] == "nosniff"
