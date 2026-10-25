from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job, JobStatus


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))

def test_queue_preserves_progress() -> None:
    item = job().model_copy(update={"progress": 25}); queue = InMemoryQueue(); queue.enqueue(item)
    assert queue.dequeue().progress == 25
