from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_metrics_has_security_headers() -> None:
    response = TestClient(create_app()).get("/metrics")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
