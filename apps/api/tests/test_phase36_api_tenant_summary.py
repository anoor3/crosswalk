from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_tenant_summary() -> None:
    c = TestClient(create_app())
    assert c.get("/reviews/summary", params={"tenant_id": "a"}).json()["total"] == 0
    assert c.get("/reviews/summary", params={"tenant_id": "b"}).json()["total"] == 0
