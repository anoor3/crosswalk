import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_error_envelope_is_frozen() -> None:
    value=ErrorEnvelope(code="x", message="m", trace_id="t")
    with pytest.raises(ValidationError): value.code="y"
