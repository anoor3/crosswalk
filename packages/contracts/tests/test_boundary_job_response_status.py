import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_job_response_preserves_status() -> None:
    assert JobResponse(id="j", status="running", progress=20).status == "running"
