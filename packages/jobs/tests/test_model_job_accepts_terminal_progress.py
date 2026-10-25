import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_accepts_full_progress() -> None:
    assert Job(id="j", tenant_id="t", kind="k", progress=100).progress == 100
