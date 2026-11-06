from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_summary_empty() -> None:
    r = TestClient(create_app()).get("/reviews/summary", params={"tenant_id": "t"})
    assert r.status_code == 200 and r.json()["total"] == 0
