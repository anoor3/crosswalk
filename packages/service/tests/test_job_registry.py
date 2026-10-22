from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_adds_and_gets_jobs() -> None:
    registry = JobRegistry()
    job = Job(id="j1", tenant_id="t1", kind="discover", created_at=datetime.now(UTC))

    assert registry.add(job) == job
    assert registry.get("j1") == job
