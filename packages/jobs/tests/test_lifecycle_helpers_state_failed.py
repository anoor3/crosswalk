from datetime import UTC, datetime

from crosswalk_jobs import Job, JobStatus

now = datetime(2026, 1, 1, tzinfo=UTC)


def make(identifier="j") -> Job:
    return Job(id=identifier, tenant_id="t", kind="sync", created_at=now)


def test_failed_state_helper() -> None:
    assert make().model_copy(update={"status": JobStatus.FAILED}).is_failed
