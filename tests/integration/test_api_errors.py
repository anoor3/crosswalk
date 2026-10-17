from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_unknown_route_is_not_successful() -> None:
    assert TestClient(create_app()).get("/does-not-exist").status_code == 404
