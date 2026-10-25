import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Job(id="j", tenant_id="t", kind="k", unknown="x")
