"""Allowlisted read-only tool contracts used by the mapping investigator."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .tools import ToolHandler, ToolRegistry, ToolSpec

READ_ONLY_TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(name="inspect_openapi", description="Inspect an OpenAPI document"),
    ToolSpec(name="inspect_endpoint", description="Inspect an endpoint response"),
    ToolSpec(name="profile_field", description="Read value profile evidence"),
    ToolSpec(name="compare_fields", description="Compare candidate fields"),
    ToolSpec(name="inspect_relationship", description="Read relationship evidence"),
    ToolSpec(name="inspect_enum", description="Read enum evidence"),
)


def register_read_only_tools(registry: ToolRegistry, handlers: Mapping[str, ToolHandler]) -> None:
    """Register only named, non-network, non-writing investigation handlers."""
    allowed = {spec.name: spec for spec in READ_ONLY_TOOL_SPECS}
    for name, handler in handlers.items():
        if name not in allowed:
            raise ValueError(f"unknown read-only tool: {name}")
        registry.register(allowed[name], handler)


def empty_read_only_output(_: Mapping[str, Any]) -> Any:
    """Placeholder handler for adapters that have not loaded a data source."""
    from .tools import ToolOutput

    return ToolOutput(summary="no evidence loaded")
