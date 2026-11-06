from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_state_filter() -> None:
    assert (
        TestClient(create_app())
        .get("/reviews", params={"tenant_id": "t", "state": "OPEN"})
        .status_code
        == 200
    )
