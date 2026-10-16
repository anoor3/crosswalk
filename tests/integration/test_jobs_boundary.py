from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job, JobStatus, run_once


def test_job_boundary_runs_a_queued_unit() -> None:
    queue = InMemoryQueue()
    queue.enqueue(Job(id="j", tenant_id="t", kind="check", created_at=datetime.now(UTC)))
    result = run_once(queue, lambda _: None, datetime.now(UTC))
    assert result is not None
    assert result.status is JobStatus.SUCCEEDED
