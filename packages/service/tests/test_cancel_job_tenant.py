from datetime import UTC, datetime

from crosswalk_service import ServiceContext, cancel_job, submit_job


def test_cancel_job_cannot_cross_tenant_boundary() -> None:
    context = ServiceContext()
    job = submit_job(context, "tenant-a", "discover", datetime.now(UTC))

    assert cancel_job(context, "tenant-b", job.id, datetime.now(UTC)) is None
    assert context.queue.contains(job.id)
