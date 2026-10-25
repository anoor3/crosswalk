from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_preserves_kind() -> None:
    job = Job(id="j1", tenant_id="t1", kind="profile", created_at=datetime.now(UTC))  # type: ignore[call-arg]
    registry = JobRegistry()
    registry.add(job)

    assert registry.get("j1").kind == "profile"  # type: ignore[union-attr]
