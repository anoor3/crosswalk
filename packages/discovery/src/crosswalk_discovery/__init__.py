"""Crosswalk OpenAPI discovery (Phase 2).

Turns an unfamiliar OpenAPI specification into a normalized, deterministic
:class:`~crosswalk_discovery.catalog.ApiCatalog`. Structural parsing only —
no LLM (PLANNER §15, CHECKER §14).

Public API::

    from crosswalk_discovery import analyze_openapi, ApiCatalog
    catalog = analyze_openapi(spec_dict)
"""

from __future__ import annotations

from .analyzer import analyze_openapi
from .catalog import (
    ApiCatalog,
    AuthScheme,
    Endpoint,
    EndpointField,
    ExternalField,
    FieldType,
    PaginationHint,
    PaginationStyle,
    UnsupportedConstruct,
)
from .errors import DiscoveryError, InvalidSpecError, RefResolutionError

__version__ = "0.1.0"

__all__ = [
    "ApiCatalog",
    "AuthScheme",
    "DiscoveryError",
    "Endpoint",
    "EndpointField",
    "ExternalField",
    "FieldType",
    "InvalidSpecError",
    "PaginationHint",
    "PaginationStyle",
    "RefResolutionError",
    "UnsupportedConstruct",
    "__version__",
    "analyze_openapi",
]
