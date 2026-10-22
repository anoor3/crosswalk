from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_removes_job() -> None:
    registry = JobRegistry()
    job = Job(id="j1", tenant_id="t1", kind="discover", created_at=datetime.now(UTC))
    registry.add(job)

    assert registry.remove("j1") == job
    assert registry.count() == 0
