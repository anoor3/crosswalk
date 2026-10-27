from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job

def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))

def test_is_empty_tracks_queue() -> None:
    q=InMemoryQueue(); assert q.is_empty(); q.enqueue(job()); assert not q.is_empty()
