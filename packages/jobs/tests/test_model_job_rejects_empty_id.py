import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_rejects_empty_id() -> None:
    with pytest.raises(ValidationError):
        Job(id="", tenant_id="t", kind="k")
