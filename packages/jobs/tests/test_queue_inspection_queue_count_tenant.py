from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_count_for_tenant() -> None:
    q = InMemoryQueue()
    q.enqueue(job("a", "t1"))
    q.enqueue(job("b", "t1"))
    q.enqueue(job("c", "t2"))
    assert q.count_for_tenant("t1") == 2
