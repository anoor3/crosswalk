from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_info_reports_service_identity() -> None:
    response = TestClient(create_app(version="1.2.3", environment="staging")).get(
        "/info"
    )

    assert response.status_code == 200
    assert response.json() == {
        "name": "crosswalk-api",
        "version": "1.2.3",
        "environment": "staging",
    }
