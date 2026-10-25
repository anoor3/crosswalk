import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_dump_contains_identity() -> None:
    data = Job(id="j", tenant_id="t", kind="k").model_dump()
    assert data["id"] == "j" and data["tenant_id"] == "t"
