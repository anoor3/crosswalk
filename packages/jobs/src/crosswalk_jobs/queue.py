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

    def __len__(self) -> int:
        return len(self._items)
