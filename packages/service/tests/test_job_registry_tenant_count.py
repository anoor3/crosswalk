from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_count_for_tenant_excludes_other_tenants() -> None:
    registry = JobRegistry()
    registry.add(Job(id="a", tenant_id="t1", kind="sync"))
    registry.add(Job(id="b", tenant_id="t1", kind="import"))
    registry.add(Job(id="c", tenant_id="t2", kind="sync"))

    assert registry.count_for_tenant("t1") == 2
    assert registry.count_for_tenant("missing") == 0
