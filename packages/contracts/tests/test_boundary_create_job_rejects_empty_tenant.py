import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_create_job_rejects_empty_tenant() -> None:
    with pytest.raises(ValidationError): CreateJobRequest(tenant_id="", kind="sync")
