from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job, JobStatus


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))

def test_queue_allows_duplicate_jobs() -> None:
    queue = InMemoryQueue(); item = job(); queue.enqueue(item); queue.enqueue(item)
    assert len(queue) == 2
