from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue
from crosswalk_service import run_job


def test_run_job_returns_none_when_queue_empty() -> None:
    result = run_job(InMemoryQueue(), lambda job: None, datetime.now(UTC))

    assert result is None
