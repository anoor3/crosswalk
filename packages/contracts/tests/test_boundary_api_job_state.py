import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_job_state_route_returns_id() -> None:
    from fastapi.testclient import TestClient
    from crosswalk_api import create_app
    assert TestClient(create_app()).get("/jobs/j/state").json()["id"] == "j"
