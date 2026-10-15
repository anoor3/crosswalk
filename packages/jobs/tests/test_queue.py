from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def test_queue_preserves_fifo_order() -> None:
    queue = InMemoryQueue()
    first = Job(id="1", tenant_id="t", kind="a", created_at=datetime.now(UTC))
    second = Job(id="2", tenant_id="t", kind="b", created_at=datetime.now(UTC))
    queue.enqueue(first)
    queue.enqueue(second)
    assert len(queue) == 2
    assert queue.dequeue() == first
    assert queue.dequeue() == second
    assert queue.dequeue() is None
