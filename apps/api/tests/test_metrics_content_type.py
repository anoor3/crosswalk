from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_metrics_is_json() -> None:
    response = TestClient(create_app()).get("/metrics")

    assert response.headers["content-type"].startswith("application/json")
