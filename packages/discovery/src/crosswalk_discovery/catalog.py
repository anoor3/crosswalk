"""The normalized internal representation produced by OpenAPI discovery.

An :class:`ApiCatalog` is Crosswalk's *deterministic* view of an external API:
its endpoints, the fields each endpoint returns/accepts (flattened with stable
JSON paths), authentication schemes, and pagination hints. Everything here is
derived mechanically from an OpenAPI document — no inference, no LLM.

Design notes
------------
* **Stable, addressable field paths.** Each :class:`ExternalField` carries a
  ``json_path`` (e.g. ``$.claimant.firstName``, ``$.partyInfo[*].roleCd``) so
  later phases (profiling, mapping, drift) can refer to a field unambiguously.
* **Uncertainty is explicit, never silent.** Constructs the parser does not
  fully model are recorded as :class:`UnsupportedConstruct` entries rather than
  dropped (CHECKER §14). A caller can inspect ``catalog.unsupported`` to see
  exactly what was not understood and where.
* **Immutable results.** Like the canonical model, catalog objects are frozen:
  a catalog is an analysis *result*, not a mutable buffer.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

_MODEL_CONFIG = ConfigDict(frozen=True, extra="forbid")


class FieldType(StrEnum):
    """Normalized field data types, independent of OpenAPI's spelling.

    OpenAPI 3.0 and 3.1 disagree on how to express some types (notably null);
    the flattener collapses both dialects onto this single vocabulary.
    """

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"
    #: Used when a schema has no usable type information at all.
    UNKNOWN = "unknown"


class ExternalField(BaseModel):
    """A single field discovered inside a request or response schema.

    Fields are *flattened*: a nested object contributes one ``ExternalField``
    per leaf and per intermediate object, each with its own ``json_path``.
    """

    model_config = _MODEL_CONFIG

    json_path: str = Field(
        description="Stable path to this field within its root schema, e.g. "
        "'$.claimant.firstName' or '$.partyInfo[*].roleCd'."
    )
    name: str = Field(description="The leaf property name (last path segment).")
    data_type: FieldType = Field(description="Normalized primary type.")
    #: Additional types when a field is a union (e.g. string|null -> types
    #: [STRING] with nullable=True; string|integer -> [STRING, INTEGER]).
    extra_types: tuple[FieldType, ...] = Field(default=())
    description: str | None = Field(default=None)
    required: bool = Field(
        default=False,
        description="True if listed in the enclosing object's `required`.",
    )
    nullable: bool = Field(
        default=False,
        description="True if the field may be null (3.0 `nullable` or 3.1 "
        "`type: null` / `anyOf` including null).",
    )
    enum_values: tuple[str, ...] = Field(
        default=(),
        description="Allowed values if the field is an enum, as strings "
        "(numeric enums are stringified). Empty when not an enum.",
    )
    format: str | None = Field(
        default=None, description="OpenAPI `format` hint, e.g. 'date-time', 'int64'."
    )
    is_array_item: bool = Field(
        default=False,
        description="True if this field is reached through an array (its "
        "json_path contains '[*]').",
    )


class EndpointField(BaseModel):
    """A path/query/header parameter of an endpoint (not a body field)."""

    model_config = _MODEL_CONFIG

    name: str
    location: str = Field(description="OpenAPI `in`: path/query/header/cookie.")
    data_type: FieldType = FieldType.UNKNOWN
    required: bool = False
    description: str | None = None


class Endpoint(BaseModel):
    """One operation: an HTTP method on a path."""

    model_config = _MODEL_CONFIG

    method: str = Field(description="Upper-case HTTP method, e.g. 'GET'.")
    path: str = Field(description="Templated path, e.g. '/claims/{claim_number}'.")
    operation_id: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: tuple[str, ...] = ()
    parameters: tuple[EndpointField, ...] = ()
    request_fields: tuple[ExternalField, ...] = Field(
        default=(), description="Flattened fields of the request body schema."
    )
    response_fields: tuple[ExternalField, ...] = Field(
        default=(),
        description="Flattened fields of the primary success response schema.",
    )
    response_status: str | None = Field(
        default=None, description="Status code the response_fields came from."
    )
    response_is_collection: bool = Field(
        default=False,
        description="True if the success response is an array at the top level.",
    )


class AuthScheme(BaseModel):
    """A security scheme declared by the API (from `components.securitySchemes`)."""

    model_config = _MODEL_CONFIG

    name: str = Field(description="The scheme's key in the spec.")
    auth_type: str = Field(description="OpenAPI `type`: apiKey/http/oauth2/openIdConnect.")
    scheme: str | None = Field(default=None, description="For http: 'bearer'/'basic'.")
    location: str | None = Field(default=None, description="For apiKey: header/query/cookie.")
    parameter_name: str | None = Field(default=None, description="For apiKey: the key name.")
    description: str | None = None


class PaginationStyle(StrEnum):
    """Detected pagination style, if any."""

    NONE = "none"
    PAGE_NUMBER = "page_number"
    OFFSET_LIMIT = "offset_limit"
    CURSOR = "cursor"


class PaginationHint(BaseModel):
    """A heuristic hint that an endpoint is paginated.

    This is a *hint*, derived deterministically from parameter names — not a
    guarantee. It surfaces evidence for later confirmation, and always records
    which parameters triggered it so the reasoning is inspectable.
    """

    model_config = _MODEL_CONFIG

    endpoint_path: str
    endpoint_method: str
    style: PaginationStyle
    parameters: tuple[str, ...] = Field(
        description="The parameter names that suggested this pagination style."
    )


class UnsupportedConstruct(BaseModel):
    """An OpenAPI construct the parser did not fully model.

    Recording these keeps discovery honest: nothing is dropped silently
    (CHECKER §14). Each entry says where it occurred and what it was.
    """

    model_config = _MODEL_CONFIG

    location: str = Field(description="Where in the spec, e.g. a JSON pointer or path.")
    construct_type: str = Field(description="Short label, e.g. 'allOf', 'circular $ref'.")
    detail: str | None = Field(default=None, description="Human-readable explanation.")


class ApiCatalog(BaseModel):
    """The complete normalized view of an external API."""

    model_config = _MODEL_CONFIG

    title: str
    version: str
    openapi_version: str
    description: str | None = None
    endpoints: tuple[Endpoint, ...] = ()
    auth_schemes: tuple[AuthScheme, ...] = ()
    pagination_hints: tuple[PaginationHint, ...] = ()
    unsupported: tuple[UnsupportedConstruct, ...] = Field(
        default=(),
        description="Constructs that were not fully modeled (explicit, not silent).",
    )

    def endpoint(self, method: str, path: str) -> Endpoint | None:
        """Look up an endpoint by method + path, or return None."""
        method_u = method.upper()
        return next(
            (e for e in self.endpoints if e.method == method_u and e.path == path),
            None,
        )
