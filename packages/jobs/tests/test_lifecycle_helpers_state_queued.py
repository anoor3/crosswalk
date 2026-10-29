from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job, JobStatus, can_transition, run_many

now=datetime(2026,1,1,tzinfo=UTC)
def make(identifier="j") -> Job:
    return Job(id=identifier, tenant_id="t", kind="sync", created_at=now)

def test_queued_state_helper() -> None:
    assert make().is_queued
