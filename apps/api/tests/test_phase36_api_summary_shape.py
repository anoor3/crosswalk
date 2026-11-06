from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_summary_shape() -> None:
    body = TestClient(create_app()).get("/reviews/summary", params={"tenant_id": "t"}).json()
    assert set(body) == {"total", "open", "confirmed", "corrected", "rejected", "unresolved"}
