from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_history_missing_tenant() -> None:
    assert TestClient(create_app()).get("/reviews/r/history").status_code == 422
