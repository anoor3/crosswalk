from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, JobStatus
from crosswalk_service import enqueue_job, run_job


def test_run_job_delegates_to_lifecycle() -> None:
    queue = InMemoryQueue()
    enqueue_job(queue, "tenant-a", "discover", datetime.now(UTC))

    result = run_job(queue, lambda job: None, datetime.now(UTC))

    assert result is not None
    assert result.status is JobStatus.SUCCEEDED
