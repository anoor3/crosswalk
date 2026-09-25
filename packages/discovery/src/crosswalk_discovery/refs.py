"""Deterministic ``$ref`` resolution for OpenAPI documents.

OpenAPI reuses schemas via local references such as
``{"$ref": "#/components/schemas/EasyClaim"}``. Resolving them is a purely
mechanical JSON-pointer lookup within the same document — no inference
(PLANNER §15).

This module intentionally supports only **local** references (those beginning
with ``#/``). External references (another file or a URL) are out of scope for
Phase 2 and raise :class:`RefResolutionError` so the limitation is loud, not
silent (CHECKER §14/§34).

Cycle handling
--------------
Recursive schemas (A -> B -> A) are legal OpenAPI and must not cause infinite
loops. The resolver itself does a single-step lookup; callers that walk a
schema tree pass a :class:`RefTracker` (or use :meth:`RefResolver.follow`) to
detect when a reference is already on the current resolution path.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import unquote

from .errors import RefResolutionError

_LOCAL_PREFIX = "#/"


def is_ref(node: Any) -> bool:
    """Return True if ``node`` is a ``$ref`` object."""
    return isinstance(node, dict) and "$ref" in node


def _decode_token(token: str) -> str:
    """Decode a single JSON-pointer token (RFC 6901 + percent-encoding).

    ``~1`` -> ``/`` and ``~0`` -> ``~``; also handles URI percent-encoding.
    """
    return unquote(token).replace("~1", "/").replace("~0", "~")


class RefResolver:
    """Resolves local ``$ref`` pointers against a single OpenAPI document."""

    def __init__(self, document: dict[str, Any]) -> None:
        self._document = document

    def resolve_ref(self, ref: str) -> dict[str, Any]:
        """Resolve one ``$ref`` string to the schema object it points at.

        Args:
            ref: A reference string, e.g. ``#/components/schemas/EasyClaim``.

        Returns:
            The referenced object (a dict).

        Raises:
            RefResolutionError: if the ref is external, malformed, points to a
                missing location, or does not resolve to an object.
        """
        if not isinstance(ref, str) or not ref:
            raise RefResolutionError(f"invalid $ref: {ref!r}")
        if not ref.startswith(_LOCAL_PREFIX):
            raise RefResolutionError(
                f"only local refs (starting with '#/') are supported; got {ref!r}"
            )

        # Walk the JSON pointer token by token.
        pointer = ref[len(_LOCAL_PREFIX) :]
        node: Any = self._document
        for raw_token in pointer.split("/"):
            token = _decode_token(raw_token)
            if isinstance(node, dict):
                if token not in node:
                    raise RefResolutionError(f"$ref not found: {ref!r} (missing '{token}')")
                node = node[token]
            elif isinstance(node, list):
                try:
                    index = int(token)
                except ValueError as exc:
                    raise RefResolutionError(
                        f"$ref {ref!r}: '{token}' is not a valid list index"
                    ) from exc
                if not 0 <= index < len(node):
                    raise RefResolutionError(f"$ref {ref!r}: index {index} out of range")
                node = node[index]
            else:
                raise RefResolutionError(
                    f"$ref {ref!r}: cannot descend into non-container at '{token}'"
                )

        if not isinstance(node, dict):
            raise RefResolutionError(f"$ref {ref!r} does not resolve to an object")
        return node

    def follow(self, node: dict[str, Any], seen: frozenset[str] = frozenset()) -> dict[str, Any]:
        """Follow a chain of refs to the first non-ref object, detecting cycles.

        If ``node`` is a ``$ref``, resolve it (and any further refs) until a
        concrete object is reached.

        Args:
            node: A schema object that may itself be a ``$ref``.
            seen: Refs already followed on this path (for cycle detection).

        Returns:
            The first concrete (non-ref) object.

        Raises:
            RefResolutionError: on a reference cycle, or any resolution error.
        """
        current = node
        visited = set(seen)
        while is_ref(current):
            ref = current["$ref"]
            if ref in visited:
                raise RefResolutionError(f"circular $ref detected: {ref!r}")
            visited.add(ref)
            current = self.resolve_ref(ref)
        return current
