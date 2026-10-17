from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_info_returns_json() -> None:
    response = TestClient(create_app()).get("/info")

    assert response.headers["content-type"].startswith("application/json")
