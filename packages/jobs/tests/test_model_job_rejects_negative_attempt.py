import pytest
from crosswalk_jobs import Job
from pydantic import ValidationError


def test_job_rejects_negative_attempt_count() -> None:
    with pytest.raises(ValidationError):
        Job(id="j", tenant_id="t", kind="k", attempt_count=-1)
