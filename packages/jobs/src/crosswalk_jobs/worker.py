from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from .models import Job, JobStatus
from .queue import InMemoryQueue
from .transitions import transition

JobHandler = Callable[[Job], None]


def run_many(
    queue: InMemoryQueue, handler: JobHandler, now: datetime, limit: int | None = None
) -> tuple[Job, ...]:
    results: list[Job] = []
    while limit is None or len(results) < limit:
        result = run_once(queue, handler, now)
        if result is None:
            break
        results.append(result)
    return tuple(results)


def run_once(queue: InMemoryQueue, handler: JobHandler, now: datetime) -> Job | None:
    """Claim one queued job, execute it, and record success or failure."""
    queued = queue.dequeue()
    if queued is None:
        return None
    running = transition(queued, JobStatus.RUNNING, now)
    try:
        handler(running)
    except Exception as error:
        return transition(running, JobStatus.FAILED, now, str(error)[:500])
    return transition(running, JobStatus.SUCCEEDED, now)
