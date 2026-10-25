from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_queue_preserves_attempt_count() -> None:
    item = job()
    item = item.model_copy(update={"attempt_count": 2})
    queue = InMemoryQueue()
    queue.enqueue(item)
    assert queue.dequeue().attempt_count == 2  # type: ignore[union-attr]
