from crosswalk_jobs import Job, JobStatus


def test_job_copy_can_update_status() -> None:
    job = Job(id="j", tenant_id="t", kind="k")
    running = job.model_copy(update={"status": JobStatus.RUNNING})
    assert running.status is JobStatus.RUNNING
