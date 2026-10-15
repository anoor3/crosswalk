"""Typed, permission-aware tool registry for investigation runs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .errors import DuplicateToolError, ToolDeniedError, ToolNotFoundError
from .models import AgentConfig

_CONFIG = ConfigDict(frozen=True, extra="forbid")
ToolHandler = Callable[[Mapping[str, Any]], "ToolOutput"]


class ToolSpec(BaseModel):
    model_config = _CONFIG

    name: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]{1,63}$")
    description: str = Field(min_length=1, max_length=500)
    requires_network: bool = False
    writes_production: bool = False
    max_request_bytes: int = Field(default=16_384, ge=1, le=1_000_000)


class ToolOutput(BaseModel):
    model_config = _CONFIG

    summary: str = Field(min_length=1, max_length=2_000)
    estimated_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0, ge=0)


class RegisteredTool:
    """A spec and handler kept together inside the process."""

    def __init__(self, spec: ToolSpec, handler: ToolHandler) -> None:
        self.spec = spec
        self.handler = handler


class ToolRegistry:
    """Allowlisted tools only; no arbitrary callable or shell execution."""

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        if spec.name in self._tools:
            raise DuplicateToolError(f"tool already registered: {spec.name}")
        self._tools[spec.name] = RegisteredTool(spec, handler)

    def get(self, name: str) -> RegisteredTool:
        try:
            return self._tools[name]
        except KeyError as error:
            raise ToolNotFoundError(f"tool not found: {name}") from error

    def allowed(self, name: str, config: AgentConfig) -> RegisteredTool:
        tool = self.get(name)
        if tool.spec.requires_network and not config.allow_network:
            raise ToolDeniedError(f"network tool denied: {name}")
        if tool.spec.writes_production and not config.allow_production_writes:
            raise ToolDeniedError(f"production-write tool denied: {name}")
        return tool

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))
