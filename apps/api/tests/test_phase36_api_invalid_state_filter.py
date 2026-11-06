from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_invalid_state_filter() -> None:
    assert (
        TestClient(create_app())
        .get("/reviews", params={"tenant_id": "t", "state": "BAD"})
        .status_code
        == 422
    )
