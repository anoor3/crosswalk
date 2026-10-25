import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_rejects_empty_tenant() -> None:
    with pytest.raises(ValidationError):
        Job(id="j", tenant_id="", kind="k")
