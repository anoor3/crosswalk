from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_ready_rejects_delete() -> None:
    assert TestClient(create_app()).delete("/ready").status_code == 405
