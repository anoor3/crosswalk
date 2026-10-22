from crosswalk_service import JobRegistry


def test_job_registry_remove_missing_returns_none() -> None:
    assert JobRegistry().remove("missing") is None
