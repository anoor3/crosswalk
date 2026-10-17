from datetime import UTC, datetime

from crosswalk_jobs import InMemoryQueue
from crosswalk_service import enqueue_job


def test_enqueue_job_preserves_tenant_and_kind() -> None:
    job = enqueue_job(InMemoryQueue(), "tenant-a", "profile", datetime.now(UTC))

    assert job.tenant_id == "tenant-a"
    assert job.kind == "profile"
