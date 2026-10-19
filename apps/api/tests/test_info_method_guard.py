from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_info_rejects_delete() -> None:
    assert TestClient(create_app()).delete("/info").status_code == 405
