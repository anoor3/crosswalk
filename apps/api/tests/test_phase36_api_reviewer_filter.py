from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_reviewer_filter() -> None:
    r = TestClient(create_app()).get("/reviews", params={"tenant_id": "t", "reviewer_id": "none"})
    assert r.status_code == 200 and r.json()["items"] == []
