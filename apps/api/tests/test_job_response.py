from crosswalk_contracts import JobResponse


def test_job_response_serializes() -> None:
    assert JobResponse(id="j1", status="queued", progress=0).progress == 0
