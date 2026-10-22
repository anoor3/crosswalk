from crosswalk_service import JobRegistry


def test_job_registry_empty_tenant_snapshot() -> None:
    assert JobRegistry().snapshot_for_tenant("tenant-a") == ()
