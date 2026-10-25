from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def test_job_registry_tenant_snapshot_reflects_update() -> None:
    created = datetime.now(UTC)
    registry = JobRegistry()
    job = Job(id="j1", tenant_id="tenant-a", kind="a", created_at=created)  # type: ignore[call-arg]
    registry.add(job)
    registry.update(job.model_copy(update={"status": JobStatus.RUNNING}))

    assert registry.snapshot_for_tenant("tenant-a")[0].status is JobStatus.RUNNING
