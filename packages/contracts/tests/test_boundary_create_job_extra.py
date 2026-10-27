import pytest
from crosswalk_contracts import CreateJobRequest
from pydantic import ValidationError


def test_create_job_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        CreateJobRequest(tenant_id="t", kind="sync", extra="x")
