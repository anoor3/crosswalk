from datetime import UTC, datetime
import pytest
from crosswalk_jobs import Job, JobStatus, transition

now = datetime(2026, 1, 1, tzinfo=UTC)

def queued() -> Job:
    return Job(id="j", tenant_id="t", kind="sync", created_at=now)

def test_failed_cannot_cancel() -> None:
    running=transition(queued(), JobStatus.RUNNING, now); failed=transition(running, JobStatus.FAILED, now)
    with pytest.raises(ValueError): transition(failed, JobStatus.CANCELLED, now)
