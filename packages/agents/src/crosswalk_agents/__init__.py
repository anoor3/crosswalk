"""Phase 8 bounded investigation-agent primitives."""

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
from .tools import RegisteredTool, ToolOutput, ToolRegistry, ToolSpec

__version__ = "0.1.0"

__all__ = [
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
]
