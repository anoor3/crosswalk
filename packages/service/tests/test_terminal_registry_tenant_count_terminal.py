from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier: str = "j", tenant: str = "t", status: JobStatus = JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)


def test_count_for_tenant_counts_terminal() -> None:
    r = JobRegistry()
    r.add(make(status=JobStatus.SUCCEEDED))
    assert r.count_for_tenant("t") == 1
