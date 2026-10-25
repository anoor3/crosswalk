import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_is_immutable() -> None:
    job = Job(id="j", tenant_id="t", kind="k")
    with pytest.raises(ValidationError):
        job.status = JobStatus.RUNNING
