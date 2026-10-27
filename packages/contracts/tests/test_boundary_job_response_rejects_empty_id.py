import pytest
from crosswalk_contracts import JobResponse
from pydantic import ValidationError


def test_job_response_rejects_empty_id() -> None:
    with pytest.raises(ValidationError):
        JobResponse(id="", status="queued", progress=0)
