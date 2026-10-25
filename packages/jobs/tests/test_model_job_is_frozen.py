import pytest
from crosswalk_jobs import Job, JobStatus
from pydantic import ValidationError


def test_job_is_immutable() -> None:
    job = Job(id="j", tenant_id="t", kind="k")  # type: ignore[misc]
    with pytest.raises(ValidationError):
        job.status = JobStatus.RUNNING  # type: ignore[misc]
