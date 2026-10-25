import pytest
from crosswalk_jobs import Job
from pydantic import ValidationError


def test_job_rejects_empty_id() -> None:
    with pytest.raises(ValidationError):
        Job(id="", tenant_id="t", kind="k")
