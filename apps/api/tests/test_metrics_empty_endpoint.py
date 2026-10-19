from crosswalk_api import Metrics, create_app
from fastapi.testclient import TestClient


def test_metrics_endpoint_starts_with_request_count() -> None:
    response = TestClient(create_app(metrics=Metrics())).get("/metrics")

    assert response.json() == {"requests.total": 1}
