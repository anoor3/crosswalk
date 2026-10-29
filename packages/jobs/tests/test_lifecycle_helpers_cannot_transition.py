from datetime import UTC, datetime
from crosswalk_jobs import InMemoryQueue, Job, JobStatus, can_transition, run_many

now=datetime(2026,1,1,tzinfo=UTC)
def make(identifier="j") -> Job:
    return Job(id=identifier, tenant_id="t", kind="sync", created_at=now)

def test_transition_guard_rejects_success_from_queue() -> None:
    assert not can_transition(make(), JobStatus.SUCCEEDED)
