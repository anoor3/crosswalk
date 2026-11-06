from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_summary_missing_tenant() -> None:
    assert TestClient(create_app()).get("/reviews/summary").status_code == 422
