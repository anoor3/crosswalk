import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_job_response_rejects_empty_id() -> None:
    with pytest.raises(ValidationError): JobResponse(id="", status="queued", progress=0)
