from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job, JobStatus, run_once


def test_worker_records_handler_failure_without_leaking_unbounded_error() -> None:
    queue = InMemoryQueue()
    job = Job(id="1", tenant_id="t", kind="discover", created_at=datetime.now(UTC))
    queue.enqueue(job)
    result = run_once(
        queue, lambda _: (_ for _ in ()).throw(RuntimeError("failure")), datetime.now(UTC)
    )
    assert result is not None
    assert result.status is JobStatus.FAILED
    assert result.error == "failure"
