from crosswalk_api import create_app
from fastapi.testclient import TestClient


def test_validation_errors_keep_trace_header() -> None:
    response = TestClient(create_app()).post(
        "/jobs", json={"tenant_id": ""}, headers={"X-Trace-Id": "error-42"}
    )

    assert response.status_code == 422
    assert response.headers["X-Trace-Id"] == "error-42"
