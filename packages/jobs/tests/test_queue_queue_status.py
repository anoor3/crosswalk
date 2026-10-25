from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job, JobStatus


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_queue_keeps_job_status() -> None:
    item = job()
    queue = InMemoryQueue()
    queue.enqueue(item)
    assert queue.dequeue().status is JobStatus.QUEUED
