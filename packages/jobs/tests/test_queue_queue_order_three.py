from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job, JobStatus


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))

def test_queue_orders_three_items() -> None:
    queue = InMemoryQueue(); items = [job(str(i)) for i in range(3)]
    for item in items: queue.enqueue(item)
    assert [queue.dequeue() for _ in items] == items
