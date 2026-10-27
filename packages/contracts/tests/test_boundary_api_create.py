import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_create_job_route_returns_created() -> None:
    from fastapi.testclient import TestClient
    from crosswalk_api import create_app
    response=TestClient(create_app()).post("/jobs", json={"tenant_id":"t","kind":"sync"})
    assert response.status_code == 201
