from datetime import UTC, datetime

from crosswalk_service import ServiceContext, run_next_job


def test_run_next_job_empty_returns_none() -> None:
    assert run_next_job(ServiceContext(), lambda _: None, datetime.now(UTC)) is None
