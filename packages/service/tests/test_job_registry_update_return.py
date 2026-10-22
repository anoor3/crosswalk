from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_update_returns_same_id() -> None:
    registry = JobRegistry()
    job = Job(id="j1", tenant_id="t1", kind="discover", created_at=datetime.now(UTC))
    registry.add(job)

    assert registry.update(job).id == "j1"
