from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_health_rejects_delete() -> None:
    assert TestClient(create_app()).delete("/health").status_code == 405
