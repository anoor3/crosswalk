from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import ServiceContext, cancel_job


def test_cancel_job_does_not_rewrite_terminal_job() -> None:
    context = ServiceContext()
    job = Job(id="done", tenant_id="tenant-a", kind="discover", status=JobStatus.SUCCEEDED)
    context.jobs.add(job)

    assert cancel_job(context, "tenant-a", job.id, datetime.now(UTC)) is None
    assert context.jobs.get(job.id) == job
