from __future__ import annotations

import ast

from crosswalk_mapping import MappingCandidate, MappingStatus

from .models import AdapterField, AdapterSpec


def adapter_spec_from_candidates(
    name: str, source_name: str, candidates: tuple[MappingCandidate, ...]
) -> AdapterSpec:
    fields = tuple(
        AdapterField(
            source_path=candidate.external_path,
            canonical_path=candidate.canonical_path,
            required=candidate.status is MappingStatus.HIGH_CONFIDENCE,
        )
        for candidate in candidates
        if candidate.canonical_path is not None
        and candidate.status in (MappingStatus.HIGH_CONFIDENCE, MappingStatus.CONFIRMED)
    )
    if not fields:
        raise ValueError("no approved or high-confidence fields can be generated")
    return AdapterSpec(name=name, source_name=source_name, fields=fields)


def generate_adapter(spec: AdapterSpec) -> str:
    """Generate a small pure function; no credentials, imports, or I/O are emitted."""
    assignments = "\n".join(
        f"    result[{field.canonical_path!r}] = payload.get({field.source_path!r})"
        for field in spec.fields
    )
    source = (
        f'"""Generated adapter for {spec.source_name}."""\n\n'
        "def transform(payload: dict[str, object]) -> dict[str, object]:\n"
        "    result: dict[str, object] = {}\n"
        f"{assignments}\n"
        "    return result\n"
    )
    ast.parse(source)
    return source
