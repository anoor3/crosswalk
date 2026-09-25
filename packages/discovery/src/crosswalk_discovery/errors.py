"""Typed errors for OpenAPI discovery.

We prefer typed exceptions over returning ``None`` or swallowing failures
(CHECKER §34). A malformed spec should fail loudly with a clear reason; an
*understood-but-unsupported* construct is different and is recorded in
``ApiCatalog.unsupported`` rather than raised.
"""

from __future__ import annotations


class DiscoveryError(Exception):
    """Base class for all discovery errors."""


class InvalidSpecError(DiscoveryError):
    """The input is not a usable OpenAPI document.

    Raised for structural problems that make analysis impossible: not a dict,
    missing ``openapi`` version, missing ``paths``, etc.
    """


class RefResolutionError(DiscoveryError):
    """A ``$ref`` could not be resolved.

    Raised when a reference points outside the document, uses an unsupported
    form (e.g. an external file), or targets a missing component.
    """
