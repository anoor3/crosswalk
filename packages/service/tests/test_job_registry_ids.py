from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_ids_preserve_insertion_order_and_tenant_scope() -> None:
    registry = JobRegistry()
    registry.add(Job(id="a", tenant_id="t1", kind="sync"))
    registry.add(Job(id="b", tenant_id="t2", kind="sync"))
    registry.add(Job(id="c", tenant_id="t1", kind="sync"))

    assert registry.ids() == ("a", "b", "c")
    assert registry.ids_for_tenant("t1") == ("a", "c")
