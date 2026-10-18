import pytest
from crosswalk_contracts import CreateJobRequest
from pydantic import ValidationError


def test_create_job_contract_requires_kind() -> None:
    with pytest.raises(ValidationError):
        CreateJobRequest(tenant_id="t1", kind="")
