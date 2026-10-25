from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def test_statuses_for_tenant_preserve_job_order() -> None:
    registry = JobRegistry()
    registry.add(Job(id="a", tenant_id="t1", kind="sync"))  # type: ignore[call-arg]
    registry.add(Job(id="b", tenant_id="t1", kind="sync", status=JobStatus.RUNNING))  # type: ignore[call-arg]
    registry.add(Job(id="c", tenant_id="t2", kind="sync", status=JobStatus.FAILED))  # type: ignore[call-arg]

    assert registry.statuses_for_tenant("t1") == (JobStatus.QUEUED, JobStatus.RUNNING)
