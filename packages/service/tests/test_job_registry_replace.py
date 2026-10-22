from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def test_job_registry_replaces_same_id() -> None:
    registry = JobRegistry()
    created = datetime.now(UTC)
    first = Job(id="j1", tenant_id="t1", kind="discover", created_at=created)
    second = first.model_copy(update={"status": JobStatus.RUNNING})
    registry.add(first)

    registry.add(second)

    assert registry.status("j1") is JobStatus.RUNNING
