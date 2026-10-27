import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_page_is_frozen() -> None:
    page=Page[int](items=(1,))
    with pytest.raises(ValidationError): page.next_cursor="x"
