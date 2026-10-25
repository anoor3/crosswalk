from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job, JobStatus


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))

def test_queue_preserves_job_identity() -> None:
    queue = InMemoryQueue(); item = job(); queue.enqueue(item)
    assert queue.dequeue() is item
