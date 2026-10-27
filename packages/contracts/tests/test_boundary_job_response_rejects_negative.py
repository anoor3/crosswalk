import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_job_response_rejects_negative_progress() -> None:
    with pytest.raises(ValidationError): JobResponse(id="j", status="queued", progress=-1)
