from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_snapshot_is_tuple() -> None:
    registry = JobRegistry()
    registry.add(Job(id="j1", tenant_id="t1", kind="discover", created_at=datetime.now(UTC)))  # type: ignore[call-arg]

    assert isinstance(registry.snapshot(), tuple)
