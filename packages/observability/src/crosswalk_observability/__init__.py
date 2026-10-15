"""Small structured observability primitives."""

from .events import Event, Metric, new_trace_id

__all__ = ["Event", "Metric", "new_trace_id"]
