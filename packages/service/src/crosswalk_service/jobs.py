from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from crosswalk_jobs import InMemoryQueue, Job, JobStatus, run_once, transition

from .context import ServiceContext


def enqueue_job(queue: InMemoryQueue, tenant_id: str, kind: str, now: datetime) -> Job:
    job = Job(id=uuid4().hex, tenant_id=tenant_id, kind=kind, created_at=now)
    queue.enqueue(job)
    return job


def submit_job(context: ServiceContext, tenant_id: str, kind: str, now: datetime) -> Job:
    job = enqueue_job(context.queue, tenant_id, kind, now)
    context.jobs.add(job)
    return job


def cancel_job(context: ServiceContext, tenant_id: str, job_id: str, now: datetime) -> Job | None:
    current = context.jobs.get_for_tenant(tenant_id, job_id)
    if current is None or not current.is_queued:
        return None
    context.queue.remove(job_id)
    cancelled = transition(current, JobStatus.CANCELLED, now)
    context.jobs.update(cancelled)
    return cancelled


def run_job(queue: InMemoryQueue, handler: Callable[[Job], None], now: datetime) -> Job | None:
    """Run one queued job through the shared lifecycle implementation."""

    return run_once(queue, handler, now)


def run_next_job(
    context: ServiceContext, handler: Callable[[Job], None], now: datetime
) -> Job | None:
    result = run_job(context.queue, handler, now)
    if result is not None:
        context.jobs.update(result)
    return result
