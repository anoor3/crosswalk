import pytest
from crosswalk_contracts import CreateJobRequest
from pydantic import ValidationError


def test_create_job_contract_is_frozen() -> None:
    request = CreateJobRequest(tenant_id="t1", kind="discover")

    with pytest.raises(ValidationError):
        request.kind = "x"  # type: ignore[misc]
