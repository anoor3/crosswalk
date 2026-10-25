from crosswalk_jobs import Job


def test_job_defaults_optional_timestamps_to_none() -> None:
    job = Job(id="j", tenant_id="t", kind="k")
    assert job.started_at is None and job.completed_at is None
