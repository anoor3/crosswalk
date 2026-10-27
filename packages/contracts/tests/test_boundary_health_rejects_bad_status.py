import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_health_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError): HealthResponse(status="bad", version="v")
