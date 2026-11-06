from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_history_missing() -> None:
    assert (
        TestClient(create_app())
        .get("/reviews/missing/history", params={"tenant_id": "t"})
        .status_code
        == 404
    )
