from crosswalk_jobs import Job


def test_job_accepts_failure_error() -> None:
    assert Job(id="j", tenant_id="t", kind="k", error="boom").error == "boom"
