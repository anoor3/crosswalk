from datetime import UTC, datetime

from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def job(identifier: str = "j", tenant_id: str = "t") -> Job:
    return Job(id=identifier, tenant_id=tenant_id, kind="sync", created_at=datetime.now(UTC))


def test_registry_has_false_after_remove() -> None:
    registry = JobRegistry()
    registry.add(job())
    registry.remove("j")
    assert not registry.has("j")
