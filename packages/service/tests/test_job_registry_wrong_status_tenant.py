from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_hides_other_tenant_status() -> None:
    registry = JobRegistry()
    registry.add(Job(id="j1", tenant_id="tenant-a", kind="discover", created_at=datetime.now(UTC)))

    assert registry.status_for_tenant("tenant-b", "j1") is None
