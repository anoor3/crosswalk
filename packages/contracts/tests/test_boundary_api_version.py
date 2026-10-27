import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_version_route_returns_service() -> None:
    from fastapi.testclient import TestClient
    from crosswalk_api import create_app
    assert TestClient(create_app()).get("/version").json()["version"] == "service"
