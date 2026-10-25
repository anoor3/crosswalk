from datetime import UTC, datetime
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))

def test_registry_count_kind_empty_zero() -> None:
    assert JobRegistry().count_by_kind("sync") == 0
