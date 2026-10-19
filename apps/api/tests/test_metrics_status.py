from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_metrics_returns_ok() -> None:
    assert TestClient(create_app()).get("/metrics").status_code == 200
