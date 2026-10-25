from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_enqueue_increments_length() -> None:
    queue = InMemoryQueue()
    queue.enqueue(job())
    assert len(queue) == 1
