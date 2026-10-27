from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus, transition

now = datetime(2026, 1, 1, tzinfo=UTC)


def queued() -> Job:
    return Job(id="j", tenant_id="t", kind="sync", created_at=now)


def test_queued_can_cancel() -> None:
    assert transition(queued(), JobStatus.CANCELLED, now).status is JobStatus.CANCELLED
