from __future__ import annotations

from datetime import datetime

from .models import Job, JobStatus

_ALLOWED: dict[JobStatus, frozenset[JobStatus]] = {
    JobStatus.QUEUED: frozenset({JobStatus.RUNNING, JobStatus.CANCELLED}),
    JobStatus.RUNNING: frozenset({JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED}),
    JobStatus.SUCCEEDED: frozenset(),
    JobStatus.FAILED: frozenset(),
    JobStatus.CANCELLED: frozenset(),
}


def transition(job: Job, status: JobStatus, now: datetime, error: str | None = None) -> Job:
    """Apply one legal lifecycle transition and stamp relevant timestamps."""
    if status not in _ALLOWED[job.status]:
        raise ValueError(f"invalid job transition: {job.status} -> {status}")
    updates: dict[str, object] = {"status": status}
    if status is JobStatus.RUNNING:
        updates.update(started_at=now, attempt_count=job.attempt_count + 1)
    if status in (JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED):
        updates.update(
            completed_at=now, progress=100 if status is JobStatus.SUCCEEDED else job.progress
        )
    if status is JobStatus.FAILED:
        updates["error"] = error or "job failed"
    return job.model_copy(update=updates)
