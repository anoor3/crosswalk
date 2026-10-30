from datetime import UTC, datetime

from crosswalk_service import ServiceContext, cancel_job, submit_job


def test_cancel_job_removes_queue_item_and_updates_registry() -> None:
    context = ServiceContext()
    job = submit_job(context, "tenant-a", "discover", datetime.now(UTC))

    cancelled = cancel_job(context, "tenant-a", job.id, datetime.now(UTC))

    assert cancelled is not None and cancelled.is_terminal
    assert context.queue.is_empty()
    assert context.jobs.get(job.id) == cancelled
