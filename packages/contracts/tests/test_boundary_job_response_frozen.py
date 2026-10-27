import pytest
from crosswalk_contracts import JobResponse
from pydantic import ValidationError


def test_job_response_is_frozen() -> None:
    response = JobResponse(id="j", status="queued", progress=0)
    with pytest.raises(ValidationError):
        response.status = "running"
