from datetime import UTC, datetime
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now=datetime(2026,1,1,tzinfo=UTC)
def make(identifier="j", tenant="t", status=JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)

def test_tenant_update_can_store_terminal() -> None:
    r=JobRegistry(); r.add(make()); done=make(status=JobStatus.SUCCEEDED); r.update_for_tenant("t",done)
    assert r.terminal_for_tenant("t") == (done,)
