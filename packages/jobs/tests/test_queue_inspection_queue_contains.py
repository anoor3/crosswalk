from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue, Job


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_contains_matches_job_id() -> None:
    q = InMemoryQueue()
    q.enqueue(job("a"))
    assert q.contains("a") and not q.contains("b")
