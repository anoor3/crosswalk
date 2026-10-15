from __future__ import annotations

import ast

from crosswalk_adapters import AdapterSpec


def generate_contract_test(spec: AdapterSpec) -> str:
    """Generate a deterministic pytest source file for required output keys."""
    checks = "\n".join(
        f"    assert {field.canonical_path!r} in transformed"
        for field in spec.fields
        if field.required
    )
    if not checks:
        checks = "    assert transformed == {} or isinstance(transformed, dict)"
    source = (
        "import pytest\n\n"
        f"def test_{spec.name}_contract(transform):\n"
        "    transformed = transform({})\n"
        f"{checks}\n"
    )
    ast.parse(source)
    return source
