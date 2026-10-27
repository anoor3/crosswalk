import pytest
from crosswalk_contracts import JobResponse
from pydantic import ValidationError


def test_job_response_rejects_progress_overflow() -> None:
    with pytest.raises(ValidationError):
        JobResponse(id="j", status="queued", progress=101)
