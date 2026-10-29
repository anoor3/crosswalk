from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier="j", tenant="t", status=JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)


def test_clear_other_tenant_keeps_terminal() -> None:
    r = JobRegistry()
    item = make("a", "t2", JobStatus.SUCCEEDED)
    r.add(make("b", "t1"))
    r.add(item)
    r.clear_for_tenant("t1")
    assert r.terminal_for_tenant("t2") == (item,)
