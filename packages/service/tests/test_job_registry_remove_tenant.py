from crosswalk_jobs import Job

from crosswalk_service import JobRegistry


def test_remove_for_tenant_cannot_remove_other_tenant_job() -> None:
    registry = JobRegistry()
    job = Job(id="j1", tenant_id="t1", kind="sync")
    registry.add(job)

    assert registry.remove_for_tenant("t2", "j1") is None
    assert registry.has("j1") is True
    assert registry.remove_for_tenant("t1", "j1") == job
