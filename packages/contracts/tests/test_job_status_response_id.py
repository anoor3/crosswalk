import pytest
from crosswalk_contracts import JobStatusResponse
from pydantic import ValidationError


def test_job_status_response_requires_id() -> None:
    with pytest.raises(ValidationError):
        JobStatusResponse(id="", status="QUEUED")
