from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_kinds_for_tenant_preserve_order() -> None:
    registry = JobRegistry()
    registry.add(Job(id="a", tenant_id="t1", kind="sync"))
    registry.add(Job(id="b", tenant_id="t1", kind="export"))
    registry.add(Job(id="c", tenant_id="t2", kind="hidden"))

    assert registry.kinds_for_tenant("t1") == ("sync", "export")
