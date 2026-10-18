from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_unknown_route_returns_not_found() -> None:
    response = TestClient(create_app()).get("/missing")

    assert response.status_code == 404
