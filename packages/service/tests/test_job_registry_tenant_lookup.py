from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_gets_job_for_tenant() -> None:
    job = Job(id="j1", tenant_id="tenant-a", kind="discover", created_at=datetime.now(UTC))
    registry = JobRegistry()
    registry.add(job)

    assert registry.get_for_tenant("tenant-a", "j1") == job
