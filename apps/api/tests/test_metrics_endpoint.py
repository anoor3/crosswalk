from crosswalk_api import Metrics, create_app
from fastapi.testclient import TestClient


def test_metrics_endpoint_reports_requests() -> None:
    metrics = Metrics()
    client = TestClient(create_app(metrics=metrics))
    client.get("/ready")

    response = client.get("/metrics")

    assert response.json()["requests.total"] == 2
