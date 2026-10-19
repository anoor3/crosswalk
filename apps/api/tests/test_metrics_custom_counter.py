from crosswalk_api import Metrics, create_app
from fastapi.testclient import TestClient


def test_metrics_endpoint_includes_custom_counter() -> None:
    metrics = Metrics()
    metrics.increment("jobs.completed")

    response = TestClient(create_app(metrics=metrics)).get("/metrics")

    assert response.json()["jobs.completed"] == 1
