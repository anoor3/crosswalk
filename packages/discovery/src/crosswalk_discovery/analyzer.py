"""Top-level OpenAPI analysis: ``analyze_openapi(spec) -> ApiCatalog``.

Deterministic structural parsing only — no LLM (PLANNER §15, CHECKER §14).
This module orchestrates the pieces:

    validate spec  ->  RefResolver  ->  per-endpoint extraction
                                        (params / request / response, flattened)
                    ->  auth schemes  ->  pagination hints  ->  ApiCatalog

Every unsupported construct discovered while flattening is aggregated into
``catalog.unsupported`` with an endpoint-scoped location, so a caller can see
exactly what was not understood and where.
"""

from __future__ import annotations

from typing import Any

from .catalog import (
    ApiCatalog,
    AuthScheme,
    Endpoint,
    EndpointField,
    ExternalField,
    FieldType,
    UnsupportedConstruct,
)
from .errors import InvalidSpecError
from .flatten import flatten_schema
from .pagination import detect_pagination
from .refs import RefResolver

# HTTP methods that carry an operation object in OpenAPI path items.
_HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")

# OpenAPI `type` string -> normalized FieldType, for scalar parameter schemas.
_PARAM_TYPE_MAP: dict[str, FieldType] = {
    "string": FieldType.STRING,
    "integer": FieldType.INTEGER,
    "number": FieldType.NUMBER,
    "boolean": FieldType.BOOLEAN,
    "array": FieldType.ARRAY,
    "object": FieldType.OBJECT,
}


def analyze_openapi(spec: dict[str, Any]) -> ApiCatalog:
    """Parse an OpenAPI 3.0/3.1 document into a normalized :class:`ApiCatalog`.

    Args:
        spec: A parsed OpenAPI document.

    Returns:
        A fully populated, frozen :class:`ApiCatalog`.

    Raises:
        InvalidSpecError: if the document is structurally unusable.
    """
    _validate_spec(spec)
    resolver = RefResolver(spec)

    info = spec.get("info", {})
    title = str(info.get("title", "Untitled API"))
    version = str(info.get("version", "0.0.0"))
    openapi_version = str(spec.get("openapi", spec.get("swagger", "unknown")))
    description = info.get("description")

    endpoints: list[Endpoint] = []
    unsupported: list[UnsupportedConstruct] = []
    pagination_hints = []

    paths = spec["paths"]
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            unsupported.append(
                UnsupportedConstruct(
                    location=f"paths.{path}",
                    construct_type="malformed path item",
                    detail="path item is not an object",
                )
            )
            continue
        # Parameters declared at the path level apply to every operation.
        shared_params = _parse_parameters(path_item.get("parameters", []), resolver)

        for method in _HTTP_METHODS:
            operation = path_item.get(method)
            if not isinstance(operation, dict):
                continue
            endpoint, ep_unsupported = _build_endpoint(
                method=method.upper(),
                path=path,
                operation=operation,
                shared_params=shared_params,
                resolver=resolver,
            )
            endpoints.append(endpoint)
            unsupported.extend(ep_unsupported)

            hint = detect_pagination(endpoint.method, path, endpoint.parameters)
            if hint is not None:
                pagination_hints.append(hint)

    auth_schemes = _parse_auth(spec, resolver)

    return ApiCatalog(
        title=title,
        version=version,
        openapi_version=openapi_version,
        description=description,
        endpoints=tuple(endpoints),
        auth_schemes=tuple(auth_schemes),
        pagination_hints=tuple(pagination_hints),
        unsupported=tuple(unsupported),
    )


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def _validate_spec(spec: Any) -> None:
    if not isinstance(spec, dict):
        raise InvalidSpecError(f"spec must be a dict, got {type(spec).__name__}")
    if "openapi" not in spec and "swagger" not in spec:
        raise InvalidSpecError("spec is missing the 'openapi' (or 'swagger') version field")
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        raise InvalidSpecError("spec is missing a 'paths' object")


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
def _build_endpoint(
    *,
    method: str,
    path: str,
    operation: dict[str, Any],
    shared_params: tuple[EndpointField, ...],
    resolver: RefResolver,
) -> tuple[Endpoint, list[UnsupportedConstruct]]:
    unsupported: list[UnsupportedConstruct] = []
    location = f"{method} {path}"

    op_params = _parse_parameters(operation.get("parameters", []), resolver)
    parameters = shared_params + op_params

    # Request body (application/json only for now).
    request_fields: tuple[ExternalField, ...] = ()
    request_schema = _json_schema_of_body(operation.get("requestBody"), resolver)
    if request_schema is not None:
        request_fields, req_unsupported = flatten_schema(request_schema, resolver)
        unsupported.extend(_prefix(req_unsupported, f"{location} requestBody"))

    # Primary success response.
    response_fields: tuple[ExternalField, ...] = ()
    response_status: str | None = None
    response_is_collection = False
    status, response_schema = _primary_success_response(operation.get("responses", {}), resolver)
    if response_schema is not None:
        response_status = status
        response_fields, resp_unsupported = flatten_schema(response_schema, resolver)
        unsupported.extend(_prefix(resp_unsupported, f"{location} response {status}"))
        response_is_collection = _is_collection_schema(response_schema, resolver)

    endpoint = Endpoint(
        method=method,
        path=path,
        operation_id=operation.get("operationId"),
        summary=operation.get("summary"),
        description=operation.get("description"),
        tags=tuple(operation.get("tags", [])),
        parameters=parameters,
        request_fields=request_fields,
        response_fields=response_fields,
        response_status=response_status,
        response_is_collection=response_is_collection,
    )
    return endpoint, unsupported


def _parse_parameters(
    raw_params: Any, resolver: RefResolver
) -> tuple[EndpointField, ...]:
    if not isinstance(raw_params, list):
        return ()
    fields: list[EndpointField] = []
    for raw in raw_params:
        param = resolver.follow(raw) if isinstance(raw, dict) else raw
        if not isinstance(param, dict) or "name" not in param:
            continue
        schema = param.get("schema", {})
        data_type = FieldType.UNKNOWN
        if isinstance(schema, dict):
            t = schema.get("type")
            if isinstance(t, str):
                data_type = _PARAM_TYPE_MAP.get(t, FieldType.UNKNOWN)
        fields.append(
            EndpointField(
                name=str(param["name"]),
                location=str(param.get("in", "query")),
                data_type=data_type,
                required=bool(param.get("required", False)),
                description=param.get("description"),
            )
        )
    return tuple(fields)


def _json_schema_of_body(
    request_body: Any, resolver: RefResolver
) -> dict[str, Any] | None:
    if not isinstance(request_body, dict):
        return None
    body = resolver.follow(request_body) if "$ref" in request_body else request_body
    content = body.get("content")
    if not isinstance(content, dict):
        return None
    media = content.get("application/json")
    if not isinstance(media, dict):
        return None
    schema = media.get("schema")
    return schema if isinstance(schema, dict) else None


def _primary_success_response(
    responses: Any, resolver: RefResolver
) -> tuple[str | None, dict[str, Any] | None]:
    """Pick the primary success response and return (status, json_schema)."""
    if not isinstance(responses, dict):
        return None, None
    # Preference order: explicit 200/201, then any other 2xx, then 'default'.
    ordered_keys = _success_status_order(responses)
    for status in ordered_keys:
        response = responses.get(status)
        if not isinstance(response, dict):
            continue
        resolved = resolver.follow(response) if "$ref" in response else response
        content = resolved.get("content")
        if not isinstance(content, dict):
            continue
        media = content.get("application/json")
        if not isinstance(media, dict):
            continue
        schema = media.get("schema")
        if isinstance(schema, dict):
            return status, schema
    return None, None


def _success_status_order(responses: dict[str, Any]) -> list[str]:
    keys = [str(k) for k in responses]
    preferred = [k for k in ("200", "201") if k in keys]
    other_2xx = sorted(k for k in keys if k.startswith("2") and k not in preferred)
    default = ["default"] if "default" in keys else []
    return preferred + other_2xx + default


def _is_collection_schema(schema: dict[str, Any], resolver: RefResolver) -> bool:
    """True if the (possibly ref'd) top-level response schema is an array."""
    resolved = resolver.follow(schema) if "$ref" in schema else schema
    t = resolved.get("type")
    if t == "array" or (isinstance(t, list) and "array" in t):
        return True
    return "items" in resolved and "properties" not in resolved


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #
def _parse_auth(spec: dict[str, Any], resolver: RefResolver) -> list[AuthScheme]:
    components = spec.get("components")
    if not isinstance(components, dict):
        return []
    schemes = components.get("securitySchemes")
    if not isinstance(schemes, dict):
        return []
    result: list[AuthScheme] = []
    for name, raw in schemes.items():
        scheme = resolver.follow(raw) if isinstance(raw, dict) and "$ref" in raw else raw
        if not isinstance(scheme, dict):
            continue
        result.append(
            AuthScheme(
                name=str(name),
                auth_type=str(scheme.get("type", "unknown")),
                scheme=scheme.get("scheme"),
                location=scheme.get("in"),
                parameter_name=scheme.get("name"),
                description=scheme.get("description"),
            )
        )
    return result


# --------------------------------------------------------------------------- #
# Utilities
# --------------------------------------------------------------------------- #
def _prefix(
    items: tuple[UnsupportedConstruct, ...], location_prefix: str
) -> list[UnsupportedConstruct]:
    """Re-scope unsupported-construct locations under an endpoint prefix."""
    return [
        item.model_copy(update={"location": f"{location_prefix} {item.location}"})
        for item in items
    ]
