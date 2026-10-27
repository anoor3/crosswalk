import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_ready_route_returns_ok() -> None:
    from fastapi.testclient import TestClient
    from crosswalk_api import create_app
    assert TestClient(create_app()).get("/ready").json()["status"] == "ok"
