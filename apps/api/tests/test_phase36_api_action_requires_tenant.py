from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_action_requires_tenant() -> None:
    assert TestClient(create_app()).get("/reviews", params={"action": "REJECT"}).status_code == 422
