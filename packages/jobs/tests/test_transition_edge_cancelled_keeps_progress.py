from datetime import UTC, datetime
import pytest
from crosswalk_jobs import Job, JobStatus, transition

now = datetime(2026, 1, 1, tzinfo=UTC)

def queued() -> Job:
    return Job(id="j", tenant_id="t", kind="sync", created_at=now)

def test_cancelled_keeps_progress() -> None:
    running=transition(queued(), JobStatus.RUNNING, now).model_copy(update={"progress": 40})
    assert transition(running, JobStatus.CANCELLED, now).progress == 40
