import ast

from crosswalk_testgen import generate_contract_test

from crosswalk_adapters import AdapterField, AdapterSpec


def test_contract_source_contains_required_key_assertions() -> None:
    source = generate_contract_test(
        AdapterSpec(
            name="claims_adapter",
            source_name="mock",
            fields=(AdapterField(source_path="id", canonical_path="claim.id", required=True),),
        )
    )
    ast.parse(source)
    assert "assert 'claim.id' in transformed" in source
    assert "import os" not in source
