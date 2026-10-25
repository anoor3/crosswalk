import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_rejects_empty_kind() -> None:
    with pytest.raises(ValidationError):
        Job(id="j", tenant_id="t", kind="")
