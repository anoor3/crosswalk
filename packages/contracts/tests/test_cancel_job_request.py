import pytest
from pydantic import ValidationError

from crosswalk_contracts import CancelJobRequest


def test_cancel_job_request_requires_tenant() -> None:
    with pytest.raises(ValidationError):
        CancelJobRequest(tenant_id="")
