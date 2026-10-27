import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_health_requires_version() -> None:
    with pytest.raises(ValidationError): HealthResponse(status="ok", version="")
