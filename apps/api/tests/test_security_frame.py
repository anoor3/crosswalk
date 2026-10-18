from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_api_sets_frame_options_header() -> None:
    response = TestClient(create_app()).get("/ready")

    assert response.headers["X-Frame-Options"] == "DENY"
