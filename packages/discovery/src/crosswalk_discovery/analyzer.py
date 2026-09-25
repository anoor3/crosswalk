"""Top-level OpenAPI analysis entry point.

NOTE: full implementation lands in Phase 2 Task 4. This module currently
exposes the public signature so the package imports cleanly; the $ref resolver
(Task 2) and schema flattener (Task 3) are built first, then wired in here.
"""

from __future__ import annotations

from typing import Any

from .catalog import ApiCatalog


def analyze_openapi(spec: dict[str, Any]) -> ApiCatalog:
    """Parse an OpenAPI document into a normalized :class:`ApiCatalog`.

    Deterministic structural parsing only — no LLM (PLANNER §15, CHECKER §14).

    Args:
        spec: A parsed OpenAPI 3.0 or 3.1 document as a dict.

    Returns:
        A fully populated :class:`ApiCatalog`.
    """
    raise NotImplementedError("analyze_openapi is implemented in Phase 2 Task 4")
