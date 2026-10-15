import pytest

from crosswalk_agents import (
    READ_ONLY_TOOL_SPECS,
    ToolOutput,
    ToolRegistry,
    register_read_only_tools,
)


def test_builtin_contracts_are_read_only_and_sorted() -> None:
    assert tuple(spec.name for spec in READ_ONLY_TOOL_SPECS) == (
        "inspect_openapi",
        "inspect_endpoint",
        "profile_field",
        "compare_fields",
        "inspect_relationship",
        "inspect_enum",
    )
    assert all(
        not spec.requires_network and not spec.writes_production for spec in READ_ONLY_TOOL_SPECS
    )


def test_registration_rejects_unlisted_handler() -> None:
    with pytest.raises(ValueError, match="unknown read-only tool"):
        register_read_only_tools(ToolRegistry(), {"shell": lambda _: ToolOutput(summary="x")})
