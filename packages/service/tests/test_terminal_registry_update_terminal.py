from datetime import UTC, datetime
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now=datetime(2026,1,1,tzinfo=UTC)
def make(identifier="j", tenant="t", status=JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)

def test_update_preserves_terminal_state() -> None:
    r=JobRegistry(); item=make(status=JobStatus.SUCCEEDED); r.add(make()); r.update(item)
    assert r.status("j") is JobStatus.SUCCEEDED
