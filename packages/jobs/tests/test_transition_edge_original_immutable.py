from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus, transition

now = datetime(2026, 1, 1, tzinfo=UTC)


def queued() -> Job:
    return Job(id="j", tenant_id="t", kind="sync", created_at=now)


def test_transition_does_not_mutate_original() -> None:
    original = queued()
    transition(original, JobStatus.RUNNING, now)
    assert original.status is JobStatus.QUEUED
