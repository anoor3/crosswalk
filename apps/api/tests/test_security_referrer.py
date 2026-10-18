from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_api_sets_referrer_policy_header() -> None:
    response = TestClient(create_app()).get("/ready")

    assert response.headers["Referrer-Policy"] == "no-referrer"
