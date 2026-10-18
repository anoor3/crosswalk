import pytest
from crosswalk_contracts import CreateJobRequest
from pydantic import ValidationError


def test_create_job_contract_rejects_extra() -> None:
    with pytest.raises(ValidationError):
        CreateJobRequest.model_validate({"tenant_id": "t1", "kind": "discover", "x": 1})
