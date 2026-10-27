from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_remove_returns_matching_job() -> None:
    q = InMemoryQueue()
    a = job("a")
    b = job("b")
    q.enqueue(a)
    q.enqueue(b)
    assert q.remove("a") is a and q.peek() is b
