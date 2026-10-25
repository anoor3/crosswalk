import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_copy_preserves_identity() -> None:
    job = Job(id="j", tenant_id="t", kind="k")
    assert job.model_copy().id == job.id
