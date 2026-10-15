"""Small structured observability primitives."""

from .events import Event, Metric, new_trace_id
from .sink import InMemorySink

__all__ = ["Event", "InMemorySink", "Metric", "new_trace_id"]
