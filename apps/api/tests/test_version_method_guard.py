from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_version_rejects_delete() -> None:
    assert TestClient(create_app()).delete("/version").status_code == 405
