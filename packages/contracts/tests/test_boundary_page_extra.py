import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_page_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError): Page[int](items=(), extra="x")
