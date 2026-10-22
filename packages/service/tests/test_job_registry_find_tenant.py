from crosswalk_jobs import Job, JobStatus

from crosswalk_service import JobRegistry


def test_find_for_tenant_optionally_filters_status() -> None:
    registry = JobRegistry()
    queued = Job(id="a", tenant_id="t1", kind="sync")
    running = Job(id="b", tenant_id="t1", kind="sync", status=JobStatus.RUNNING)
    registry.add(queued)
    registry.add(running)
    registry.add(Job(id="c", tenant_id="t2", kind="sync"))

    assert registry.find_for_tenant("t1") == (queued, running)
    assert registry.find_for_tenant("t1", JobStatus.RUNNING) == (running,)
