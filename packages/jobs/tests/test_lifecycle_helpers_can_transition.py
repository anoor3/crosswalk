from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus, can_transition

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier="j") -> Job:
    return Job(id=identifier, tenant_id="t", kind="sync", created_at=now)


def test_transition_guard_allows_running() -> None:
    assert can_transition(make(), JobStatus.RUNNING)
