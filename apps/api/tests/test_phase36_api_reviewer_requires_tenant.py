from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_reviewer_requires_tenant() -> None:
    assert TestClient(create_app()).get("/reviews", params={"reviewer_id": "a"}).status_code == 422
