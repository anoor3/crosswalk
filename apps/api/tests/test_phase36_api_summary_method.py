from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_summary_method() -> None:
    assert (
        TestClient(create_app()).post("/reviews/summary", params={"tenant_id": "t"}).status_code
        == 405
    )
