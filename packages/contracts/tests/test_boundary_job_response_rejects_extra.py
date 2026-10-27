import pytest
from crosswalk_contracts import JobResponse
from pydantic import ValidationError


def test_job_response_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        JobResponse(id="j", status="queued", progress=0, extra="x")  # type: ignore[call-arg]
