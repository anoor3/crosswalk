from crosswalk_jobs import Job


def test_job_defaults_to_zero_attempts() -> None:
    assert Job(id="j", tenant_id="t", kind="k").attempt_count == 0
