from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_snapshot_preserves_insert_order() -> None:
    registry = JobRegistry()
    created = datetime.now(UTC)
    registry.add(Job(id="first", tenant_id="t1", kind="a", created_at=created))
    registry.add(Job(id="second", tenant_id="t1", kind="b", created_at=created))

    assert [job.id for job in registry.snapshot()] == ["first", "second"]
