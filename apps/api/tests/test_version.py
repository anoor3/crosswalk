from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_version_endpoint_is_machine_readable() -> None:
    payload = TestClient(create_app()).get("/version").json()
    assert payload["status"] == "ok"
    assert payload["version"] == "service"
