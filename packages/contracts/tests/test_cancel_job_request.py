import pytest
from crosswalk_contracts import CancelJobRequest
from pydantic import ValidationError


def test_cancel_job_request_requires_tenant() -> None:
    with pytest.raises(ValidationError):
        CancelJobRequest(tenant_id="")
