from datetime import UTC, datetime

from crosswalk_jobs import Job

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier: str = "j") -> Job:
    return Job(id=identifier, tenant_id="t", kind="sync", created_at=now)


def test_queued_state_helper() -> None:
    assert make().is_queued
