from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_snapshots_one_tenant() -> None:
    created = datetime.now(UTC)
    registry = JobRegistry()
    first = Job(id="j1", tenant_id="tenant-a", kind="a", created_at=created)
    second = Job(id="j2", tenant_id="tenant-b", kind="b", created_at=created)
    registry.add(first)
    registry.add(second)

    assert registry.snapshot_for_tenant("tenant-a") == (first,)
