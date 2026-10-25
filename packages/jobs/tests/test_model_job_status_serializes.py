import pytest
from pydantic import ValidationError
from crosswalk_jobs import Job, JobStatus

def test_job_status_serializes_as_string() -> None:
    assert Job(id="j", tenant_id="t", kind="k").model_dump()["status"] is JobStatus.QUEUED
