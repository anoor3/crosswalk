from crosswalk_agents import (
    AgentConfig,
    InvestigationAgent,
    InvestigationStatus,
    ToolCallStatus,
    ToolInvocation,
    ToolOutput,
    ToolRegistry,
    ToolSpec,
)


def registry_for(spec: ToolSpec, output: ToolOutput) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(spec, lambda _: output)
    return registry


def invocation(name: str = "inspect_schema") -> ToolInvocation:
    return ToolInvocation(name, {"field": "customer_id"}, "inspect customer id")


def test_read_only_plan_completes_with_audit_record() -> None:
    registry = registry_for(
        ToolSpec(name="inspect_schema", description="Read schema"),
        ToolOutput(summary="schema inspected", estimated_tokens=4, estimated_cost_usd=0.01),
    )
    result = InvestigationAgent(registry).run("map customer id", [invocation()])
    assert result.status is InvestigationStatus.COMPLETED
    assert result.tool_history[0].status is ToolCallStatus.SUCCEEDED
    assert result.estimated_tokens == 4


def test_network_tool_is_denied_by_default() -> None:
    registry = registry_for(
        ToolSpec(name="fetch_remote", description="Fetch remote data", requires_network=True),
        ToolOutput(summary="should not run"),
    )
    result = InvestigationAgent(registry).run("inspect", [invocation("fetch_remote")])
    assert result.status is InvestigationStatus.FAILED
    assert result.tool_history[0].status is ToolCallStatus.DENIED


def test_iteration_bound_stops_remaining_steps() -> None:
    registry = registry_for(
        ToolSpec(name="inspect_schema", description="Read schema"), ToolOutput(summary="ok")
    )
    config = AgentConfig(max_iterations=1)
    result = InvestigationAgent(registry, config).run("inspect", [invocation(), invocation()])
    assert result.status is InvestigationStatus.TIMED_OUT
    assert result.iterations == 1


def test_token_budget_stops_after_successful_call() -> None:
    registry = registry_for(
        ToolSpec(name="inspect_schema", description="Read schema"),
        ToolOutput(summary="large", estimated_tokens=11),
    )
    result = InvestigationAgent(registry, AgentConfig(token_budget=10)).run(
        "inspect", [invocation()]
    )
    assert result.status is InvestigationStatus.BUDGET_EXCEEDED


def test_handler_failure_is_redacted_from_result() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(name="inspect_schema", description="Read schema"),
        lambda _: (_ for _ in ()).throw(RuntimeError("secret-token")),
    )
    result = InvestigationAgent(registry).run("inspect", [invocation()])
    assert result.status is InvestigationStatus.FAILED
    assert "secret-token" not in result.model_dump_json()
