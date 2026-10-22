from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def test_filter_counts_match_registered_jobs() -> None:
    registry = JobRegistry()
    registry.add(Job(id="a", tenant_id="t1", kind="sync"))
    registry.add(Job(id="b", tenant_id="t1", kind="sync", status=JobStatus.RUNNING))
    registry.add(Job(id="c", tenant_id="t2", kind="export"))

    assert registry.count_by_status(JobStatus.QUEUED) == 2
    assert registry.count_by_kind("sync") == 2
    assert registry.count_by_kind("missing") == 0
