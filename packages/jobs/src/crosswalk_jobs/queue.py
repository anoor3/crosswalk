from __future__ import annotations

from collections import deque

from .models import Job


class InMemoryQueue:
    """Deterministic queue seam; a broker adapter can implement the same methods."""

    def __init__(self) -> None:
        self._items: deque[Job] = deque()

    def enqueue(self, job: Job) -> None:
        self._items.append(job)

    def dequeue(self) -> Job | None:
        return self._items.popleft() if self._items else None

    def peek(self) -> Job | None:
        return self._items[0] if self._items else None

    def clear(self) -> int:
        count = len(self._items)
        self._items.clear()
        return count

    def snapshot(self) -> tuple[Job, ...]:
        return tuple(self._items)

    def contains(self, job_id: str) -> bool:
        return any(job.id == job_id for job in self._items)

    def ids(self) -> tuple[str, ...]:
        return tuple(job.id for job in self._items)

    def for_tenant(self, tenant_id: str) -> tuple[Job, ...]:
        return tuple(job for job in self._items if job.tenant_id == tenant_id)

    def count_for_tenant(self, tenant_id: str) -> int:
        return sum(job.tenant_id == tenant_id for job in self._items)

    def remove(self, job_id: str) -> Job | None:
        for index, job in enumerate(self._items):
            if job.id == job_id:
                del self._items[index]
                return job
        return None

    def __len__(self) -> int:
        return len(self._items)
