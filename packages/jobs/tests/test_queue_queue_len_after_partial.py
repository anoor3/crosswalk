from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_queue_length_after_partial_drain() -> None:
    queue = InMemoryQueue()
    queue.enqueue(job("a"))
    queue.enqueue(job("b"))
    queue.dequeue()
    assert len(queue) == 1
