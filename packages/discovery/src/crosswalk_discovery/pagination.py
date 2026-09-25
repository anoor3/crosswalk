"""Deterministic pagination-hint detection.

Pagination style is *hinted* by an endpoint's query-parameter names. This is a
heuristic — not a guarantee — so the result is a :class:`PaginationHint` that
always records which parameters triggered it, keeping the reasoning inspectable
(CHECKER §14: nothing hidden). No LLM: it is pure name matching (PLANNER §15).
"""

from __future__ import annotations

from collections.abc import Iterable

from .catalog import EndpointField, PaginationHint, PaginationStyle

# Lower-cased parameter names that suggest each style. Ordered by specificity:
# cursor/offset styles are checked before the more generic page-number style.
_CURSOR_NAMES = {"cursor", "after", "before", "next", "page_token", "pagetoken"}
_OFFSET_NAMES = {"offset", "skip", "start"}
_LIMIT_NAMES = {"limit", "per_page", "perpage", "page_size", "pagesize", "size", "count"}
_PAGE_NAMES = {"page", "page_number", "pagenumber", "pagenum"}


def detect_pagination(
    method: str, path: str, parameters: Iterable[EndpointField]
) -> PaginationHint | None:
    """Return a pagination hint for an endpoint, or None if none is detected.

    Only query parameters are considered. The first matching style wins in
    order cursor -> offset+limit -> page-number, because a cursor or offset is
    a stronger signal than a bare ``page``.
    """
    query_names = {p.name.lower() for p in parameters if p.location == "query"}
    if not query_names:
        return None

    cursor_hits = sorted(query_names & _CURSOR_NAMES)
    offset_hits = sorted(query_names & _OFFSET_NAMES)
    limit_hits = sorted(query_names & _LIMIT_NAMES)
    page_hits = sorted(query_names & _PAGE_NAMES)

    if cursor_hits:
        triggers = cursor_hits + limit_hits
        return _hint(method, path, PaginationStyle.CURSOR, triggers)
    if offset_hits:
        triggers = offset_hits + limit_hits
        return _hint(method, path, PaginationStyle.OFFSET_LIMIT, triggers)
    if page_hits:
        triggers = page_hits + limit_hits
        return _hint(method, path, PaginationStyle.PAGE_NUMBER, triggers)
    return None


def _hint(method: str, path: str, style: PaginationStyle, triggers: list[str]) -> PaginationHint:
    return PaginationHint(
        endpoint_path=path,
        endpoint_method=method,
        style=style,
        parameters=tuple(triggers),
    )
