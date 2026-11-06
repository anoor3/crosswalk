from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_invalid_action_filter() -> None:
    assert (
        TestClient(create_app())
        .get("/reviews", params={"tenant_id": "t", "action": "BAD"})
        .status_code
        == 422
    )
