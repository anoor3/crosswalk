from crosswalk_contracts import JobStatusResponse


def test_job_status_response_serializes() -> None:
    value = JobStatusResponse(id="j1", status="QUEUED")

    assert value.model_dump() == {"id": "j1", "status": "QUEUED"}
