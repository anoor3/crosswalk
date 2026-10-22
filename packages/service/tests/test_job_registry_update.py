from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def test_job_registry_updates_existing_job() -> None:
    registry = JobRegistry()
    created = datetime.now(UTC)
    job = Job(id="j1", tenant_id="t1", kind="discover", created_at=created)
    registry.add(job)
    running = job.model_copy(update={"status": JobStatus.RUNNING})

    assert registry.update(running).status is JobStatus.RUNNING
