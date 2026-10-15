"""Bounded execution loop for typed investigation plans."""

from __future__ import annotations

import json
import time
from collections.abc import Mapping, Sequence
from typing import Any

from .errors import AgentError, ToolDeniedError
from .models import (
    AgentConfig,
    InvestigationResult,
    InvestigationStatus,
    ToolCallRecord,
    ToolCallStatus,
)
from .safety import redact_summary
from .tools import ToolRegistry


class ToolInvocation:
    """A validated request for one registered tool."""

    def __init__(self, tool_name: str, request: Mapping[str, Any], summary: str) -> None:
        if not tool_name.strip():
            raise ValueError("tool_name must not be empty")
        if not summary.strip():
            raise ValueError("summary must not be empty")
        self.tool_name = tool_name
        self.request = dict(request)
        self.summary = summary[:1000]


class InvestigationAgent:
    """Execute a finite, allowlisted investigation plan with an audit trail."""

    def __init__(self, registry: ToolRegistry, config: AgentConfig | None = None) -> None:
        self.registry = registry
        self.config = config or AgentConfig()

    def run(self, goal: str, steps: Sequence[ToolInvocation]) -> InvestigationResult:
        if not goal.strip():
            raise ValueError("goal must not be empty")
        started = time.monotonic()
        history: list[ToolCallRecord] = []
        total_tokens = 0
        total_cost = 0.0
        status = InvestigationStatus.COMPLETED
        for iteration, invocation in enumerate(steps, start=1):
            if (
                iteration > self.config.max_iterations
                or time.monotonic() - started >= self.config.timeout_seconds
            ):
                status = InvestigationStatus.TIMED_OUT
                break
            try:
                tool = self.registry.allowed(invocation.tool_name, self.config)
                encoded = json.dumps(invocation.request, sort_keys=True, default=str).encode(
                    "utf-8"
                )
                if len(encoded) > tool.spec.max_request_bytes:
                    raise AgentError("request exceeds tool size limit")
                before = time.monotonic()
                output = tool.handler(invocation.request)
                history.append(
                    ToolCallRecord(
                        iteration=iteration,
                        tool_name=invocation.tool_name,
                        status=ToolCallStatus.SUCCEEDED,
                        request_summary=redact_summary(invocation.summary),
                        response_summary=redact_summary(output.summary, 2000),
                        latency_ms=(time.monotonic() - before) * 1000,
                        estimated_tokens=output.estimated_tokens,
                        estimated_cost_usd=output.estimated_cost_usd,
                    )
                )
                total_tokens += output.estimated_tokens
                total_cost += output.estimated_cost_usd
                if (
                    total_tokens > self.config.token_budget
                    or total_cost > self.config.cost_budget_usd
                ):
                    status = InvestigationStatus.BUDGET_EXCEEDED
                    break
            except ToolDeniedError as exc:
                history.append(
                    ToolCallRecord(
                        iteration=iteration,
                        tool_name=invocation.tool_name,
                        status=ToolCallStatus.DENIED,
                        request_summary=redact_summary(invocation.summary),
                        response_summary=redact_summary(str(exc)),
                        latency_ms=0,
                    )
                )
                status = InvestigationStatus.FAILED
                break
            except Exception:
                history.append(
                    ToolCallRecord(
                        iteration=iteration,
                        tool_name=invocation.tool_name,
                        status=ToolCallStatus.FAILED,
                        request_summary=redact_summary(invocation.summary),
                        response_summary="tool execution failed",
                        latency_ms=0,
                    )
                )
                status = InvestigationStatus.FAILED
                break
        rationale = {
            InvestigationStatus.COMPLETED: "All planned read-only steps completed.",
            InvestigationStatus.TIMED_OUT: (
                "The investigation exceeded its time or iteration bound."
            ),
            InvestigationStatus.BUDGET_EXCEEDED: (
                "The investigation exceeded its configured budget."
            ),
            InvestigationStatus.FAILED: "A tool was denied or failed; human review is required.",
            InvestigationStatus.NEEDS_REVIEW: "Human review is required before approval.",
        }[status]
        unresolved = (
            ()
            if status is InvestigationStatus.COMPLETED
            else ("Human review is required before approval.",)
        )
        return InvestigationResult(
            goal=goal,
            status=status,
            rationale=rationale,
            unresolved_questions=unresolved,
            tool_history=tuple(history),
            iterations=len(history),
            estimated_tokens=total_tokens,
            estimated_cost_usd=total_cost,
        )
