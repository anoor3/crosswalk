from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus, transition

now = datetime(2026, 1, 1, tzinfo=UTC)


def queued() -> Job:
    return Job(id="j", tenant_id="t", kind="sync", created_at=now)


def test_retry_increments_existing_attempt() -> None:
    original = queued().model_copy(update={"attempt_count": 2})
    assert transition(original, JobStatus.RUNNING, now).attempt_count == 3
