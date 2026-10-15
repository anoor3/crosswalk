from datetime import UTC, datetime

import pytest
from crosswalk_jobs import Job, JobStatus, transition


def test_job_lifecycle_stamps_attempt_and_completion() -> None:
    created = datetime(2026, 1, 1, tzinfo=UTC)
    started = datetime(2026, 1, 1, 0, 1, tzinfo=UTC)
    finished = datetime(2026, 1, 1, 0, 2, tzinfo=UTC)
    job = Job(id="j1", tenant_id="t1", kind="discover", created_at=created)
    job = transition(job, JobStatus.RUNNING, started)
    job = transition(job, JobStatus.SUCCEEDED, finished)
    assert job.attempt_count == 1
    assert job.completed_at == finished
    assert job.progress == 100


def test_terminal_jobs_cannot_restart() -> None:
    job = Job(id="j1", tenant_id="t1", kind="discover", created_at=datetime.now(UTC))
    job = transition(job, JobStatus.CANCELLED, datetime.now(UTC))
    with pytest.raises(ValueError, match="invalid job transition"):
        transition(job, JobStatus.RUNNING, datetime.now(UTC))
