from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_queue_is_fifo() -> None:
    queue = InMemoryQueue()
    first = job("a")
    second = job("b")
    queue.enqueue(first)
    queue.enqueue(second)
    assert queue.dequeue() == first
