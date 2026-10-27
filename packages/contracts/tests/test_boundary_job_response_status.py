from crosswalk_contracts import JobResponse


def test_job_response_preserves_status() -> None:
    assert JobResponse(id="j", status="running", progress=20).status == "running"
