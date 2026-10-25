from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_clear_for_tenant_preserves_other_tenants() -> None:
    registry = JobRegistry()
    registry.add(Job(id="a", tenant_id="t1", kind="sync"))
    other = Job(id="b", tenant_id="t2", kind="sync")
    registry.add(other)

    assert registry.clear_for_tenant("t1") == 1
    assert registry.snapshot() == (other,)
