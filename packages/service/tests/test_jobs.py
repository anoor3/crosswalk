from datetime import UTC, datetime

from crosswalk_service import ServiceContext, enqueue_job


def test_enqueue_job_uses_context_queue() -> None:
    context = ServiceContext()
    job = enqueue_job(context.queue, "tenant", "discover", datetime.now(UTC))
    assert context.queue.dequeue() == job
