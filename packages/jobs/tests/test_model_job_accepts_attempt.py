import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_accepts_positive_attempt_count() -> None:
    assert Job(id="j", tenant_id="t", kind="k", attempt_count=2).attempt_count == 2
