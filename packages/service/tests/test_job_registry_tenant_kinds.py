from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_kinds_for_tenant_preserve_order() -> None:
    registry = JobRegistry()
    registry.add(Job(id="a", tenant_id="t1", kind="sync"))  # type: ignore[call-arg]
    registry.add(Job(id="b", tenant_id="t1", kind="export"))  # type: ignore[call-arg]
    registry.add(Job(id="c", tenant_id="t2", kind="hidden"))  # type: ignore[call-arg]

    assert registry.kinds_for_tenant("t1") == ("sync", "export")
