import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_defaults_to_zero_progress() -> None:
    assert Job(id="j", tenant_id="t", kind="k").progress == 0
