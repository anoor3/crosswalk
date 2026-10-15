"""Typed agent and tool failures."""

from __future__ import annotations


class AgentError(ValueError):
    """Base agent-domain error."""


class DuplicateToolError(AgentError):
    """A tool name was registered twice."""


class ToolNotFoundError(AgentError):
    """A requested tool is not registered."""


class ToolDeniedError(AgentError):
    """The run permissions do not allow this tool."""


class InvalidToolRequestError(AgentError):
    """Tool request data violates the registered contract."""
