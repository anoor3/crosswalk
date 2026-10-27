import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_error_envelope_rejects_long_message() -> None:
    with pytest.raises(ValidationError): ErrorEnvelope(code="x", message="x"*1001, trace_id="t")
