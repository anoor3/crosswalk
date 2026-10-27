import pytest
from crosswalk_contracts import CreateJobRequest
from pydantic import ValidationError


def test_create_job_rejects_empty_tenant() -> None:
    with pytest.raises(ValidationError):
        CreateJobRequest(tenant_id="", kind="sync")
