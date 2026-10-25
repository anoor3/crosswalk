from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job, JobStatus


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))

def test_queue_preserves_different_tenants() -> None:
    queue = InMemoryQueue(); first = job("a", "t1"); second = job("b", "t2"); queue.enqueue(first); queue.enqueue(second)
    assert queue.dequeue().tenant_id == "t1" and queue.dequeue().tenant_id == "t2"
