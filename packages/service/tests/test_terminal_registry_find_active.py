from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier: str = "j", tenant: str = "t", status: JobStatus = JobStatus.QUEUED) -> Job:
    return Job(id=identifier, tenant_id=tenant, kind="sync", status=status, created_at=now)


def test_find_for_tenant_can_find_running() -> None:
    r = JobRegistry()
    item = make(status=JobStatus.RUNNING)
    r.add(item)
    assert r.find_for_tenant("t", JobStatus.RUNNING) == (item,)
