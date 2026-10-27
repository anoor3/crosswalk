import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_job_response_is_frozen() -> None:
    response=JobResponse(id="j", status="queued", progress=0)
    with pytest.raises(ValidationError): response.status="running"
