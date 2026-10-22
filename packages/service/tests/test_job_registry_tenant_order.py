from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_tenant_snapshot_preserves_order() -> None:
    created = datetime.now(UTC)
    registry = JobRegistry()
    registry.add(Job(id="j1", tenant_id="tenant-a", kind="a", created_at=created))
    registry.add(Job(id="j2", tenant_id="tenant-a", kind="b", created_at=created))

    assert [job.id for job in registry.snapshot_for_tenant("tenant-a")] == ["j1", "j2"]
