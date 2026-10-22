import pytest
from crosswalk_contracts import TenantJobLookup
from pydantic import ValidationError


def test_tenant_job_lookup_requires_job_id() -> None:
    with pytest.raises(ValidationError):
        TenantJobLookup(tenant_id="tenant-a", job_id="")
