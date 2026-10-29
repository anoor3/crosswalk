from datetime import UTC, datetime
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now=datetime(2026,1,1,tzinfo=UTC)
def make(identifier="j", tenant="t", status=JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)

def test_terminal_for_tenant_isolates_tenant() -> None:
    r=JobRegistry(); r.add(make("a","t1",JobStatus.SUCCEEDED)); r.add(make("b","t2",JobStatus.SUCCEEDED))
    assert r.terminal_for_tenant("t1")[0].tenant_id == "t1"
