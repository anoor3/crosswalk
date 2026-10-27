from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_clear_returns_removed_count() -> None:
    q = InMemoryQueue()
    q.enqueue(job("a"))
    q.enqueue(job("b"))
    assert q.clear() == 2 and q.is_empty()
