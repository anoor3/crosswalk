from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_history_method() -> None:
    assert (
        TestClient(create_app()).post("/reviews/r/history", params={"tenant_id": "t"}).status_code
        == 405
    )
