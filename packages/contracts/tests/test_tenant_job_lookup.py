from crosswalk_contracts import TenantJobLookup


def test_tenant_job_lookup_serializes() -> None:
    value = TenantJobLookup(tenant_id="tenant-a", job_id="j1")

    assert value.model_dump() == {"tenant_id": "tenant-a", "job_id": "j1"}
