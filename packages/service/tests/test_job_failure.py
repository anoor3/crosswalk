from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, JobStatus
from crosswalk_service import enqueue_job, run_job


def test_run_job_reports_handler_failure() -> None:
    queue = InMemoryQueue()
    enqueue_job(queue, "tenant-a", "discover", datetime.now(UTC))

    result = run_job(
        queue,
        lambda job: (_ for _ in ()).throw(RuntimeError("boom")),
        datetime.now(UTC),
    )

    assert result is not None
    assert result.status is JobStatus.FAILED
