from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_repeated_empty_dequeue_is_safe() -> None:
    queue = InMemoryQueue()
    assert queue.dequeue() is None
    assert queue.dequeue() is None
