from crosswalk_jobs import Job, JobStatus

from crosswalk_service import JobRegistry


def test_filters_preserve_registration_order() -> None:
    registry = JobRegistry()
    first = Job(id="a", tenant_id="t1", kind="sync")
    second = Job(id="b", tenant_id="t2", kind="sync", status=JobStatus.RUNNING)
    third = Job(id="c", tenant_id="t1", kind="export")
    registry.add(first)
    registry.add(second)
    registry.add(third)

    assert registry.find_by_status(JobStatus.QUEUED) == (first, third)
    assert registry.find_by_kind("sync") == (first, second)
