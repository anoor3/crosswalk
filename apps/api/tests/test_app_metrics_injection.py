from crosswalk_api import Metrics, create_app
from fastapi.testclient import TestClient


def test_app_uses_injected_metrics() -> None:
    metrics = Metrics()
    client = TestClient(create_app(metrics=metrics))
    client.get("/health")

    assert metrics.snapshot()["requests.total"] == 1
