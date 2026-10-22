from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def test_job_registry_snapshot_reflects_update() -> None:
    job = Job(id="j1", tenant_id="t1", kind="discover", created_at=datetime.now(UTC))
    registry = JobRegistry()
    registry.add(job)
    registry.update(job.model_copy(update={"status": JobStatus.RUNNING}))

    assert registry.snapshot()[0].status is JobStatus.RUNNING
