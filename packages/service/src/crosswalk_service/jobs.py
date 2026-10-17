from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from crosswalk_jobs import InMemoryQueue, Job, run_once


def enqueue_job(queue: InMemoryQueue, tenant_id: str, kind: str, now: datetime) -> Job:
    job = Job(id=uuid4().hex, tenant_id=tenant_id, kind=kind, created_at=now)
    queue.enqueue(job)
    return job


def run_job(queue: InMemoryQueue, handler: Callable[[Job], None], now: datetime) -> Job | None:
    """Run one queued job through the shared lifecycle implementation."""

    return run_once(queue, handler, now)
