from crosswalk_contracts import JobResponse


def test_job_response_accepts_progress_boundaries() -> None:
    assert JobResponse(id="j", status="queued", progress=0).progress == 0
    assert JobResponse(id="k", status="done", progress=100).progress == 100
