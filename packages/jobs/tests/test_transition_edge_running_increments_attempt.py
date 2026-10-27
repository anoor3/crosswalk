from datetime import UTC, datetime
import pytest
from crosswalk_jobs import Job, JobStatus, transition

now = datetime(2026, 1, 1, tzinfo=UTC)

def queued() -> Job:
    return Job(id="j", tenant_id="t", kind="sync", created_at=now)

def test_running_increments_attempt() -> None:
    assert transition(queued(), JobStatus.RUNNING, now).attempt_count == 1
