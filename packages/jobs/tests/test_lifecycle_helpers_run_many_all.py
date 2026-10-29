from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job, run_many

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier="j") -> Job:
    return Job(id=identifier, tenant_id="t", kind="sync", created_at=now)


def test_run_many_drains_without_limit() -> None:
    q = InMemoryQueue()
    q.enqueue_many((make("a"), make("b")))
    assert len(run_many(q, lambda _: None, now)) == 2 and q.is_empty()
