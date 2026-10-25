from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job, JobStatus


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))

def test_queue_can_drain_all_items() -> None:
    queue = InMemoryQueue(); queue.enqueue(job("a")); queue.enqueue(job("b")); queue.dequeue(); queue.dequeue()
    assert queue.dequeue() is None
