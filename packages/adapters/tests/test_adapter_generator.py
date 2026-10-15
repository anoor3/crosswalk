import ast

import pytest

from crosswalk_adapters import AdapterField, AdapterSpec, generate_adapter


def test_generated_adapter_is_pure_and_parseable() -> None:
    source = generate_adapter(
        AdapterSpec(
            name="claims_adapter",
            source_name="mock_api",
            fields=(AdapterField(source_path="claim_id", canonical_path="claim.id"),),
        )
    )
    tree = ast.parse(source)
    assert [node.name for node in tree.body if isinstance(node, ast.FunctionDef)] == ["transform"]
    assert "result['claim.id'] = payload.get('claim_id')" in source
    assert "password" not in source.lower()


def test_empty_adapter_fields_are_rejected() -> None:
    with pytest.raises(ValueError, match="fields"):
        AdapterSpec(name="empty_adapter", source_name="source", fields=())
