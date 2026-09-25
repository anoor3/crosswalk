"""Unit tests for the $ref resolver (Phase 2 Task 2)."""

from __future__ import annotations

from typing import Any

import pytest

from crosswalk_discovery.errors import RefResolutionError
from crosswalk_discovery.refs import RefResolver, is_ref


@pytest.fixture
def document() -> dict[str, Any]:
    return {
        "components": {
            "schemas": {
                "Claim": {
                    "type": "object",
                    "properties": {"claimant": {"$ref": "#/components/schemas/Party"}},
                },
                "Party": {"type": "object", "properties": {"name": {"type": "string"}}},
                # A self-referential (cyclic) schema.
                "Node": {
                    "type": "object",
                    "properties": {"next": {"$ref": "#/components/schemas/Node"}},
                },
                # A ref-to-ref chain: Alias -> Party.
                "Alias": {"$ref": "#/components/schemas/Party"},
                # Escaped token: a key literally named "a/b".
            },
            "weird": {"a/b": {"type": "string"}},
        }
    }


class TestIsRef:
    def test_detects_ref(self) -> None:
        assert is_ref({"$ref": "#/x"}) is True

    def test_non_ref(self) -> None:
        assert is_ref({"type": "string"}) is False
        assert is_ref("not a dict") is False
        assert is_ref(None) is False


class TestResolveRef:
    def test_basic(self, document: dict[str, Any]) -> None:
        r = RefResolver(document)
        party = r.resolve_ref("#/components/schemas/Party")
        assert party["type"] == "object"
        assert "name" in party["properties"]

    def test_escaped_slash_token(self, document: dict[str, Any]) -> None:
        # "~1" decodes to "/", so this addresses the key "a/b".
        r = RefResolver(document)
        node = r.resolve_ref("#/components/weird/a~1b")
        assert node == {"type": "string"}

    def test_external_ref_rejected(self, document: dict[str, Any]) -> None:
        r = RefResolver(document)
        with pytest.raises(RefResolutionError, match="only local refs"):
            r.resolve_ref("other.json#/components/schemas/Party")

    def test_missing_target(self, document: dict[str, Any]) -> None:
        r = RefResolver(document)
        with pytest.raises(RefResolutionError, match="not found"):
            r.resolve_ref("#/components/schemas/DoesNotExist")

    def test_empty_ref_rejected(self, document: dict[str, Any]) -> None:
        r = RefResolver(document)
        with pytest.raises(RefResolutionError):
            r.resolve_ref("")

    def test_non_object_target(self) -> None:
        r = RefResolver({"x": {"y": "scalar"}})
        with pytest.raises(RefResolutionError, match="does not resolve to an object"):
            r.resolve_ref("#/x/y")


class TestFollow:
    def test_follow_non_ref_returns_same(self, document: dict[str, Any]) -> None:
        r = RefResolver(document)
        node = {"type": "string"}
        assert r.follow(node) == node

    def test_follow_single_ref(self, document: dict[str, Any]) -> None:
        r = RefResolver(document)
        resolved = r.follow({"$ref": "#/components/schemas/Party"})
        assert resolved["type"] == "object"

    def test_follow_ref_chain(self, document: dict[str, Any]) -> None:
        # Alias -> Party.
        r = RefResolver(document)
        resolved = r.follow({"$ref": "#/components/schemas/Alias"})
        assert "name" in resolved["properties"]

    def test_direct_cycle_detected(self) -> None:
        # A -> A must not loop forever.
        doc = {"components": {"schemas": {"A": {"$ref": "#/components/schemas/A"}}}}
        r = RefResolver(doc)
        with pytest.raises(RefResolutionError, match="circular"):
            r.follow({"$ref": "#/components/schemas/A"})

    def test_indirect_cycle_detected(self) -> None:
        # A -> B -> A.
        doc = {
            "components": {
                "schemas": {
                    "A": {"$ref": "#/components/schemas/B"},
                    "B": {"$ref": "#/components/schemas/A"},
                }
            }
        }
        r = RefResolver(doc)
        with pytest.raises(RefResolutionError, match="circular"):
            r.follow({"$ref": "#/components/schemas/A"})

    def test_self_referential_object_is_not_a_follow_cycle(
        self, document: dict[str, Any]
    ) -> None:
        # Node's ref is nested under properties, so following Node itself
        # resolves to a concrete object without a cycle. (The cycle only
        # appears when a walker recurses into properties, which is the
        # flattener's job in Task 3.)
        r = RefResolver(document)
        node = r.follow({"$ref": "#/components/schemas/Node"})
        assert node["type"] == "object"
