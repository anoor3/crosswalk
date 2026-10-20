from collections.abc import Mapping
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class EventLog:
    """Process-local structured event collector for the local API boundary."""

    _events: list[dict[str, str]] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock)

    def record(self, event: str, fields: Mapping[str, str] | None = None) -> None:
        payload = {"event": event, **(dict(fields) if fields else {})}
        with self._lock:
            self._events.append(payload)

    def snapshot(self) -> tuple[dict[str, str], ...]:
        with self._lock:
            return tuple(dict(event) for event in self._events)
