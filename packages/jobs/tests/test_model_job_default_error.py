from crosswalk_jobs import Job


def test_job_defaults_error_to_none() -> None:
    assert Job(id="j", tenant_id="t", kind="k").error is None
