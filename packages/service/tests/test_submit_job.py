from datetime import UTC, datetime

from crosswalk_service import ServiceContext, submit_job


def test_submit_job_registers_and_enqueues_same_job() -> None:
    context = ServiceContext()
    job = submit_job(context, "tenant-a", "discover", datetime.now(UTC))

    assert context.jobs.get(job.id) is job
    assert context.queue.peek() is job
