from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_metrics_rejects_post() -> None:
    assert TestClient(create_app()).post("/metrics").status_code == 405
