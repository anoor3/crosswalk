"""Edge-case unit tests for analyze_openapi (Phase 2 Task 5).

The generated fixtures are all clean OpenAPI 3.1 and don't exercise every
construct the parser must handle. These synthetic specs cover the gaps:
OpenAPI 3.0 `nullable`, enums, numeric enums, oneOf unions, circular $ref,
auth schemes, pagination styles, and invalid specs. Nothing here touches the
mock APIs — they are minimal hand-written documents.
"""

from __future__ import annotations

from typing import Any

import pytest

from crosswalk_discovery import (
    PaginationStyle,
    analyze_openapi,
)
from crosswalk_discovery.errors import InvalidSpecError


def _spec(paths: dict[str, Any], **extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "openapi": "3.1.0",
        "info": {"title": "T", "version": "1.0.0"},
        "paths": paths,
    }
    base.update(extra)
    return base


def _get_response_fields(spec: dict[str, Any], path: str) -> dict[str, Any]:
    cat = analyze_openapi(spec)
    endpoint = cat.endpoint("GET", path)
    assert endpoint is not None
    return {f.json_path: f for f in endpoint.response_fields}


def _json_response(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "responses": {
            "200": {
                "description": "ok",
                "content": {"application/json": {"schema": schema}},
            }
        }
    }


# --------------------------------------------------------------------------- #
# Spec validation
# --------------------------------------------------------------------------- #
class TestValidation:
    def test_not_a_dict(self) -> None:
        with pytest.raises(InvalidSpecError, match="must be a dict"):
            analyze_openapi("nope")  # type: ignore[arg-type]

    def test_missing_version(self) -> None:
        with pytest.raises(InvalidSpecError, match="version"):
            analyze_openapi({"paths": {}})

    def test_missing_paths(self) -> None:
        with pytest.raises(InvalidSpecError, match="paths"):
            analyze_openapi({"openapi": "3.1.0"})

    def test_swagger_2_version_accepted_structurally(self) -> None:
        # We don't fully support 2.0, but a structurally valid doc should parse
        # (its version is recorded) rather than crash.
        cat = analyze_openapi({"swagger": "2.0", "paths": {}})
        assert cat.openapi_version == "2.0"


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class TestEnums:
    def test_string_enum(self) -> None:
        schema = {
            "type": "object",
            "properties": {"status": {"type": "string", "enum": ["OPEN", "CLOSED"]}},
        }
        fields = _get_response_fields(_spec({"/x": {"get": _json_response(schema)}}), "/x")
        assert fields["$.status"].enum_values == ("OPEN", "CLOSED")

    def test_numeric_enum(self) -> None:
        schema = {
            "type": "object",
            "properties": {"state": {"type": "integer", "enum": [1, 2, 3]}},
        }
        fields = _get_response_fields(_spec({"/x": {"get": _json_response(schema)}}), "/x")
        assert fields["$.state"].enum_values == ("1", "2", "3")


# --------------------------------------------------------------------------- #
# Nullable dialects
# --------------------------------------------------------------------------- #
class TestNullable:
    def test_openapi_30_nullable(self) -> None:
        schema = {
            "type": "object",
            "properties": {"note": {"type": "string", "nullable": True}},
        }
        spec = _spec({"/x": {"get": _json_response(schema)}}, openapi="3.0.3")
        fields = _get_response_fields(spec, "/x")
        assert fields["$.note"].nullable is True


# --------------------------------------------------------------------------- #
# Unions
# --------------------------------------------------------------------------- #
class TestUnions:
    def test_oneof_union_flagged(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "value": {"oneOf": [{"type": "string"}, {"type": "integer"}]}
            },
        }
        cat = analyze_openapi(_spec({"/x": {"get": _json_response(schema)}}))
        assert any(u.construct_type == "oneOf" for u in cat.unsupported)


# --------------------------------------------------------------------------- #
# Circular $ref
# --------------------------------------------------------------------------- #
class TestCircularRef:
    def test_cycle_terminates_and_is_recorded(self) -> None:
        spec = _spec(
            {"/x": {"get": _json_response({"$ref": "#/components/schemas/Node"})}},
            components={
                "schemas": {
                    "Node": {
                        "type": "object",
                        "properties": {"next": {"$ref": "#/components/schemas/Node"}},
                    }
                }
            },
        )
        cat = analyze_openapi(spec)  # must not hang
        assert any(u.construct_type == "circular $ref" for u in cat.unsupported)


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #
class TestAuth:
    def test_apikey_and_bearer(self) -> None:
        spec = _spec(
            {"/x": {"get": _json_response({"type": "object"})}},
            components={
                "securitySchemes": {
                    "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                    "BearerAuth": {"type": "http", "scheme": "bearer"},
                }
            },
        )
        cat = analyze_openapi(spec)
        by_name = {a.name: a for a in cat.auth_schemes}
        assert by_name["ApiKeyAuth"].auth_type == "apiKey"
        assert by_name["ApiKeyAuth"].location == "header"
        assert by_name["ApiKeyAuth"].parameter_name == "X-API-Key"
        assert by_name["BearerAuth"].scheme == "bearer"


# --------------------------------------------------------------------------- #
# Pagination
# --------------------------------------------------------------------------- #
class TestPagination:
    def _paginated(self, params: list[dict[str, Any]]) -> Any:
        spec = _spec(
            {
                "/items": {
                    "get": {
                        "parameters": params,
                        **_json_response({"type": "array", "items": {"type": "string"}}),
                    }
                }
            }
        )
        return analyze_openapi(spec)

    def test_page_number_style(self) -> None:
        cat = self._paginated(
            [
                {"name": "page", "in": "query", "schema": {"type": "integer"}},
                {"name": "limit", "in": "query", "schema": {"type": "integer"}},
            ]
        )
        assert len(cat.pagination_hints) == 1
        assert cat.pagination_hints[0].style is PaginationStyle.PAGE_NUMBER

    def test_offset_style(self) -> None:
        cat = self._paginated(
            [
                {"name": "offset", "in": "query", "schema": {"type": "integer"}},
                {"name": "limit", "in": "query", "schema": {"type": "integer"}},
            ]
        )
        assert cat.pagination_hints[0].style is PaginationStyle.OFFSET_LIMIT

    def test_cursor_style(self) -> None:
        cat = self._paginated(
            [{"name": "cursor", "in": "query", "schema": {"type": "string"}}]
        )
        assert cat.pagination_hints[0].style is PaginationStyle.CURSOR

    def test_no_pagination_when_no_query_params(self) -> None:
        cat = self._paginated(
            [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]
        )
        assert cat.pagination_hints == ()


# --------------------------------------------------------------------------- #
# Request body
# --------------------------------------------------------------------------- #
class TestRequestBody:
    def test_request_fields_flattened(self) -> None:
        spec = _spec(
            {
                "/items": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["name"],
                                        "properties": {"name": {"type": "string"}},
                                    }
                                }
                            }
                        },
                        **_json_response({"type": "object"}),
                    }
                }
            }
        )
        cat = analyze_openapi(spec)
        endpoint = cat.endpoint("POST", "/items")
        assert endpoint is not None
        by = {f.json_path: f for f in endpoint.request_fields}
        assert by["$.name"].required is True
