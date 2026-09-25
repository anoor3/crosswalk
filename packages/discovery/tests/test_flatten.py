"""Unit tests for the schema flattener (Phase 2 Task 3)."""

from __future__ import annotations

from typing import Any

from crosswalk_discovery.catalog import ExternalField, FieldType, UnsupportedConstruct
from crosswalk_discovery.flatten import flatten_schema
from crosswalk_discovery.refs import RefResolver


def _flatten(
    schema: dict[str, Any], document: dict[str, Any] | None = None
) -> tuple[tuple[ExternalField, ...], tuple[UnsupportedConstruct, ...]]:
    resolver = RefResolver(document or {})
    return flatten_schema(schema, resolver)


def _by_path(fields: Any) -> dict[str, Any]:
    return {f.json_path: f for f in fields}


class TestPrimitives:
    def test_string_leaf(self) -> None:
        fields, unsupported = _flatten({"type": "string", "description": "hi"})
        assert unsupported == ()
        assert len(fields) == 1
        assert fields[0].data_type is FieldType.STRING
        assert fields[0].description == "hi"

    def test_format_captured(self) -> None:
        fields, _ = _flatten({"type": "string", "format": "date-time"})
        assert fields[0].format == "date-time"

    def test_unknown_type(self) -> None:
        fields, _ = _flatten({"title": "mystery"})
        assert fields[0].data_type is FieldType.UNKNOWN


class TestEnum:
    def test_string_enum(self) -> None:
        fields, _ = _flatten({"type": "string", "enum": ["OPEN", "CLOSED"]})
        assert fields[0].enum_values == ("OPEN", "CLOSED")

    def test_numeric_enum_stringified(self) -> None:
        fields, _ = _flatten({"type": "integer", "enum": [1, 2, 3]})
        assert fields[0].enum_values == ("1", "2", "3")


class TestNullable:
    def test_openapi_30_nullable(self) -> None:
        fields, _ = _flatten({"type": "string", "nullable": True})
        assert fields[0].nullable is True

    def test_openapi_31_type_list_null(self) -> None:
        fields, _ = _flatten({"type": ["string", "null"]})
        assert fields[0].data_type is FieldType.STRING
        assert fields[0].nullable is True

    def test_anyof_string_or_null(self) -> None:
        fields, unsupported = _flatten(
            {"anyOf": [{"type": "string"}, {"type": "null"}]}
        )
        assert unsupported == ()  # string|null is a clean nullable, not unsupported
        assert fields[0].data_type is FieldType.STRING
        assert fields[0].nullable is True


class TestMultiType:
    def test_type_list_multi(self) -> None:
        fields, _ = _flatten({"type": ["string", "integer"]})
        assert fields[0].data_type is FieldType.STRING
        assert fields[0].extra_types == (FieldType.INTEGER,)

    def test_genuine_union_flagged_but_explored(self) -> None:
        fields, unsupported = _flatten(
            {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        )
        assert any(u.construct_type == "oneOf" for u in unsupported)
        assert len(fields) == 1  # first branch explored


class TestObjectsAndArrays:
    def test_nested_object_paths(self) -> None:
        schema = {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string"},
                "claimant": {
                    "type": "object",
                    "required": ["firstName"],
                    "properties": {
                        "firstName": {"type": "string"},
                        "age": {"type": "integer"},
                    },
                },
            },
        }
        fields, unsupported = _flatten(schema)
        assert unsupported == ()
        by = _by_path(fields)
        assert by["$"].data_type is FieldType.OBJECT
        assert by["$.id"].required is True
        assert by["$.claimant"].data_type is FieldType.OBJECT
        assert by["$.claimant.firstName"].required is True
        assert by["$.claimant.age"].required is False

    def test_array_of_scalars(self) -> None:
        fields, _ = _flatten({"type": "array", "items": {"type": "string"}})
        by = _by_path(fields)
        assert by["$"].data_type is FieldType.ARRAY
        assert by["$[*]"].data_type is FieldType.STRING
        assert by["$[*]"].is_array_item is True

    def test_array_of_objects(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "partyInfo": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"roleCd": {"type": "string"}},
                    },
                }
            },
        }
        fields, _ = _flatten(schema)
        by = _by_path(fields)
        assert by["$.partyInfo"].data_type is FieldType.ARRAY
        assert by["$.partyInfo[*].roleCd"].data_type is FieldType.STRING
        assert by["$.partyInfo[*].roleCd"].is_array_item is True

    def test_additional_properties_flagged(self) -> None:
        _, unsupported = _flatten(
            {"type": "object", "additionalProperties": {"type": "string"}}
        )
        assert any("additionalProperties" in u.construct_type for u in unsupported)


class TestRefs:
    def test_ref_resolved_and_flattened(self) -> None:
        document = {
            "components": {
                "schemas": {
                    "Party": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    }
                }
            }
        }
        schema = {
            "type": "object",
            "properties": {"claimant": {"$ref": "#/components/schemas/Party"}},
        }
        fields, unsupported = _flatten(schema, document)
        assert unsupported == ()
        by = _by_path(fields)
        assert by["$.claimant"].data_type is FieldType.OBJECT
        assert by["$.claimant.name"].data_type is FieldType.STRING

    def test_unresolved_ref_recorded(self) -> None:
        schema = {"type": "object", "properties": {"x": {"$ref": "#/nope/missing"}}}
        _, unsupported = _flatten(schema, {})
        assert any(u.construct_type == "unresolved $ref" for u in unsupported)

    def test_circular_ref_recorded_not_looped(self) -> None:
        document = {
            "components": {
                "schemas": {
                    "Node": {
                        "type": "object",
                        "properties": {"next": {"$ref": "#/components/schemas/Node"}},
                    }
                }
            }
        }
        schema = {"$ref": "#/components/schemas/Node"}
        fields, unsupported = _flatten(schema, document)
        # It terminates (no infinite loop) and records the cycle explicitly.
        assert any(u.construct_type == "circular $ref" for u in unsupported)
        by = _by_path(fields)
        assert "$" in by  # the outer Node object was emitted


class TestAllOf:
    def test_allof_flagged_and_merged(self) -> None:
        schema = {
            "allOf": [
                {"type": "object", "properties": {"a": {"type": "string"}}},
                {"type": "object", "properties": {"b": {"type": "integer"}}},
            ]
        }
        fields, unsupported = _flatten(schema)
        assert any(u.construct_type == "allOf" for u in unsupported)
        by = _by_path(fields)
        # Best-effort: both branches' properties discovered.
        assert "$.a" in by
        assert "$.b" in by
