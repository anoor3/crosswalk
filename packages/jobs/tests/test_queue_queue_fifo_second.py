from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_queue_returns_second_after_first() -> None:
    queue = InMemoryQueue()
    queue.enqueue(job("a"))
    second = job("b")
    queue.enqueue(second)
    queue.dequeue()
    assert queue.dequeue() == second
