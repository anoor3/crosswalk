from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_for_tenant_isolated() -> None:
    q = InMemoryQueue()
    a = job("a", "t1")
    b = job("b", "t2")
    q.enqueue(a)
    q.enqueue(b)
    assert q.for_tenant("t1") == (a,)
