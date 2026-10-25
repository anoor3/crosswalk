import pytest
from crosswalk_jobs import Job
from pydantic import ValidationError


def test_job_rejects_empty_kind() -> None:
    with pytest.raises(ValidationError):
        Job(id="j", tenant_id="t", kind="")
