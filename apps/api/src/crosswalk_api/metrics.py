from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Metrics:
    """Small thread-safe request counter for local observability."""

    _counts: dict[str, int] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def increment(self, name: str) -> None:
        with self._lock:
            self._counts[name] = self._counts.get(name, 0) + 1

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counts)
