import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_error_envelope_requires_code() -> None:
    with pytest.raises(ValidationError): ErrorEnvelope(code="", message="m", trace_id="t")
