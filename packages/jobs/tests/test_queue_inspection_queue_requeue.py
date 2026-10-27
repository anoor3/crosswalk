from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_requeue_places_job_first() -> None:
    q = InMemoryQueue()
    a = job("a")
    b = job("b")
    q.enqueue(a)
    q.enqueue(b)
    q.requeue(b)
    assert q.dequeue() is b
