import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_create_job_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError): CreateJobRequest(tenant_id="t", kind="sync", extra="x")
