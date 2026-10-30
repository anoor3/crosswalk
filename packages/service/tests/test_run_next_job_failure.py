from datetime import UTC, datetime

from crosswalk_jobs import JobStatus
from crosswalk_service import ServiceContext, run_next_job, submit_job


def test_run_next_job_persists_failed_worker_result() -> None:
    context = ServiceContext()
    job = submit_job(context, "tenant-a", "discover", datetime.now(UTC))

    result = run_next_job(
        context, lambda _: (_ for _ in ()).throw(RuntimeError("boom")), datetime.now(UTC)
    )

    assert result is not None and result.status is JobStatus.FAILED
    assert context.jobs.status(job.id) is JobStatus.FAILED
