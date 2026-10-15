"""Phase 8 bounded investigation-agent primitives."""

from .builtin import READ_ONLY_TOOL_SPECS, register_read_only_tools
from .errors import (
    AgentError,
    DuplicateToolError,
    InvalidToolRequestError,
    ToolDeniedError,
    ToolNotFoundError,
)
from .models import (
    AgentConfig,
    InvestigationResult,
    InvestigationStatus,
    ToolCallRecord,
    ToolCallStatus,
)
from .runner import InvestigationAgent, ToolInvocation
from .safety import redact_summary
from .tools import RegisteredTool, ToolOutput, ToolRegistry, ToolSpec

__version__ = "0.1.0"

__all__ = [
    "READ_ONLY_TOOL_SPECS",
    "AgentConfig",
    "AgentError",
    "DuplicateToolError",
    "InvalidToolRequestError",
    "InvestigationAgent",
    "InvestigationResult",
    "InvestigationStatus",
    "RegisteredTool",
    "ToolCallRecord",
    "ToolCallStatus",
    "ToolDeniedError",
    "ToolInvocation",
    "ToolNotFoundError",
    "ToolOutput",
    "ToolRegistry",
    "ToolSpec",
    "__version__",
    "redact_summary",
    "register_read_only_tools",
]
