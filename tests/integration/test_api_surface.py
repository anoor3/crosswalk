from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_api_surface_exposes_operational_routes() -> None:
    client = TestClient(create_app("integration"))
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
    assert client.get("/version").status_code == 200
