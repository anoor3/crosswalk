from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job, run_many

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier: str = "j") -> Job:
    return Job(id=identifier, tenant_id="t", kind="sync", created_at=now)


def test_run_many_empty_returns_tuple() -> None:
    assert run_many(InMemoryQueue(), lambda _: None, now) == ()
