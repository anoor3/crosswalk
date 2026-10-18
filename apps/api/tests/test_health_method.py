from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_health_rejects_post_method() -> None:
    response = TestClient(create_app()).post("/health")

    assert response.status_code == 405
