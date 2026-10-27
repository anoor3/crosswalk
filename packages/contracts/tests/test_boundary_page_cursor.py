import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_page_preserves_cursor() -> None:
    assert Page[int](items=(1,), next_cursor="next").next_cursor == "next"
