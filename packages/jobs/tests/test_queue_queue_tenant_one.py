from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_queue_keeps_tenant_on_job() -> None:
    item = job()
    queue = InMemoryQueue()
    queue.enqueue(item)
    assert queue.dequeue().tenant_id == "t"
