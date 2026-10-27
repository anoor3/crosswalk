from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_peek_does_not_remove_head() -> None:
    q = InMemoryQueue()
    item = job()
    q.enqueue(item)
    assert q.peek() is item and len(q) == 1
