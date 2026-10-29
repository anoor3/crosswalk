from datetime import UTC, datetime
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now=datetime(2026,1,1,tzinfo=UTC)
def make(identifier="j", tenant="t", status=JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)

def test_remove_for_tenant_removes_terminal() -> None:
    r=JobRegistry(); item=make(status=JobStatus.CANCELLED); r.add(item)
    assert r.remove_for_tenant("t","j") == item
