from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier="j", tenant="t", status=JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)


def test_clear_for_tenant_removes_terminal_same_tenant() -> None:
    r = JobRegistry()
    r.add(make(status=JobStatus.SUCCEEDED))
    assert r.clear_for_tenant("t") == 1
