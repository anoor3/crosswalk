from crosswalk_jobs import Job, JobStatus


def test_job_defaults_to_queued() -> None:
    assert Job(id="j", tenant_id="t", kind="k").status is JobStatus.QUEUED
