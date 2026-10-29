from datetime import UTC, datetime
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now=datetime(2026,1,1,tzinfo=UTC)
def make(identifier="j", tenant="t", status=JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)

def test_snapshot_tuple_is_stable() -> None:
    r=JobRegistry(); item=make(status=JobStatus.SUCCEEDED); r.add(item); first=r.snapshot(); r.remove("j")
    assert first == (item,)
