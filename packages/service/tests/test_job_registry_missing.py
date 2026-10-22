from crosswalk_service import JobRegistry


def test_job_registry_returns_none_for_missing_job() -> None:
    assert JobRegistry().get("missing") is None
