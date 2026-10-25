import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_rejects_progress_over_hundred() -> None:
    with pytest.raises(ValidationError):
        Job(id="j", tenant_id="t", kind="k", progress=101)
