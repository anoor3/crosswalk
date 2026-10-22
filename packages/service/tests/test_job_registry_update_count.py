from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def test_job_registry_update_does_not_change_count() -> None:
    registry = JobRegistry()
    job = Job(id="j1", tenant_id="t1", kind="discover", created_at=datetime.now(UTC))
    registry.add(job)
    registry.update(job.model_copy(update={"status": JobStatus.RUNNING}))

    assert registry.count() == 1
