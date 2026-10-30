from datetime import UTC, datetime

from crosswalk_jobs import JobStatus
from crosswalk_service import ServiceContext, run_next_job, submit_job


def test_run_next_job_updates_registry_success() -> None:
    context = ServiceContext()
    job = submit_job(context, "tenant-a", "discover", datetime.now(UTC))

    result = run_next_job(context, lambda _: None, datetime.now(UTC))

    assert result is not None and result.id == job.id
    assert context.jobs.status(job.id) is JobStatus.SUCCEEDED
