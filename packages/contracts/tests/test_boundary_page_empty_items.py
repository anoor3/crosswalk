import pytest
from pydantic import ValidationError
from crosswalk_contracts import CreateJobRequest, ErrorEnvelope, HealthResponse, JobResponse, Page

def test_page_accepts_empty_items() -> None:
    page=Page[int](items=())
    assert page.items == () and page.next_cursor is None
