"""Derive target fields from the canonical Python models, never benchmark labels.

Python annotations retain information that a JSON Schema ``anyOf`` can obscure:
``Decimal`` is money, ``date`` is a date, and enums carry their vocabulary. The
catalog walks those annotations in declaration order and emits scalar leaves.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from functools import lru_cache
from types import UnionType
from typing import Union, get_args, get_origin

from pydantic import BaseModel

from crosswalk_canonical import Claim
from crosswalk_discovery import FieldType
from crosswalk_profiler import SemanticType

from .models import CanonicalField


def _non_null_type(annotation: object) -> tuple[object, bool]:
    if get_origin(annotation) in (UnionType, Union):
        members = get_args(annotation)
        non_null = tuple(member for member in members if member is not type(None))
        if len(non_null) != 1:
            raise TypeError(f"Unsupported canonical union: {annotation!r}")
        return non_null[0], len(non_null) != len(members)
    return annotation, False


def _scalar_type(annotation: object, name: str) -> tuple[FieldType, SemanticType, tuple[str, ...]]:
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        values = tuple(str(member.value) for member in annotation)
        return FieldType.STRING, SemanticType.ENUM_CANDIDATE, values
    if annotation in (date, datetime):
        return FieldType.STRING, SemanticType.DATE, ()
    if annotation is Decimal:
        return FieldType.NUMBER, SemanticType.CURRENCY, ()
    if annotation is bool:
        return FieldType.BOOLEAN, SemanticType.BOOLEAN, ()
    if annotation in (int, float):
        kind = FieldType.INTEGER if annotation is int else FieldType.NUMBER
        return kind, SemanticType.NUMBER, ()
    if annotation is str:
        # The canonical model explicitly names identifier fields this way;
        # this rule does not inspect external source names or benchmark labels.
        semantic = (
            SemanticType.IDENTIFIER if name.endswith(("_id", "_number")) else SemanticType.UNKNOWN
        )
        return FieldType.STRING, semantic, ()
    raise TypeError(f"Unsupported canonical scalar: {annotation!r}")


def _walk(
    model: type[BaseModel], prefix: str, ancestor_description: str = ""
) -> tuple[CanonicalField, ...]:
    fields: list[CanonicalField] = []
    for name, definition in model.model_fields.items():
        annotation, nullable = _non_null_type(definition.annotation)
        path = f"{prefix}.{name}"
        description = definition.description or ""
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            fields.extend(_walk(annotation, path, description))
            continue
        data_type, semantic_type, enum_values = _scalar_type(annotation, name)
        context_description = " ".join(part for part in (ancestor_description, description) if part)
        fields.append(
            CanonicalField(
                path=path,
                name=name,
                data_type=data_type,
                description=context_description,
                semantic_type=semantic_type,
                nullable=nullable,
                enum_values=enum_values,
            )
        )
    return tuple(fields)


@lru_cache(maxsize=1)
def canonical_fields() -> tuple[CanonicalField, ...]:
    """Return the immutable scalar target catalog derived from ``Claim``.

    Nested person roles keep their distinct paths and parent descriptions.
    Adding a supported field to the canonical models adds it here automatically;
    unsupported annotations fail explicitly rather than disappearing silently.
    """
    return _walk(Claim, "claim")
