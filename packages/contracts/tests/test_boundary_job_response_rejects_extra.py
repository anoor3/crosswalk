import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_job_response_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError): JobResponse(id="j", status="queued", progress=0, extra="x")
