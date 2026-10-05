"""Deterministic enum hypotheses and guarded runtime translation."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from math import sqrt

from .errors import (
    InvalidEnumVocabularyError,
    UnapprovedEnumMappingError,
    UnknownEnumValueError,
)
from .models import EnumMappingResult, EnumMappingStatus, EnumValueCandidate

_WORDS = re.compile(r"[a-z0-9]+")
_ALIASES: dict[str, tuple[str, ...]] = {
    "opn": ("open",),
    "pnd": ("pending",),
    "cls": ("closed",),
    "rpn": ("reopened",),
    "reopen": ("reopened",),
}


def _as_values(values: Sequence[str | int], name: str) -> tuple[str, ...]:
    result = tuple(str(value) for value in values)
    if not result or any(not value.strip() for value in result):
        raise InvalidEnumVocabularyError(f"{name} must contain non-empty values")
    if len(result) != len(set(result)):
        raise InvalidEnumVocabularyError(f"{name} must contain unique values")
    return result


def _tokens(value: str) -> frozenset[str]:
    return frozenset(
        token for word in _WORDS.findall(value.lower()) for token in _ALIASES.get(word, (word,))
    )


def _similarity(left: str, right: str) -> tuple[float, str] | None:
    if left == right:
        return 1.0, "Exact enum value match."
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if left_tokens and left_tokens == right_tokens:
        return 0.95, "Conservative documented abbreviation normalization matched the value."
    if not left_tokens or not right_tokens:
        return None
    overlap = len(left_tokens & right_tokens) / sqrt(len(left_tokens) * len(right_tokens))
    return (overlap, "Normalized enum token overlap matched the value.") if overlap >= 0.5 else None


def _description_similarity(left: str, right: str) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / sqrt(len(left_tokens) * len(right_tokens))


def map_enum_values(
    external_values: Sequence[str | int],
    canonical_values: Sequence[str],
    *,
    observed_values: Sequence[str | int] = (),
    external_descriptions: Mapping[str, str] | None = None,
    canonical_descriptions: Mapping[str, str] | None = None,
    explicit_mapping: Mapping[str | int, str] | None = None,
) -> EnumMappingResult:
    """Build a complete, inspectable mapping without coercing unknown values.

    ``explicit_mapping`` represents a caller-supplied documentation/config
    decision and is marked ``CONFIRMED``. Otherwise this function only applies
    conservative lexical evidence; numeric codes with no matching evidence stay
    ``UNKNOWN``. Observed values outside the declared source vocabulary are
    returned in ``unseen_values`` and cannot be translated.
    """
    source = _as_values(external_values, "external_values")
    target = _as_values(canonical_values, "canonical_values")
    source_descriptions = external_descriptions or {}
    target_descriptions = canonical_descriptions or {}
    explicit = {str(key): value for key, value in (explicit_mapping or {}).items()}
    invalid_explicit = set(explicit) - set(source)
    if invalid_explicit or any(value not in target for value in explicit.values()):
        raise InvalidEnumVocabularyError(
            "explicit mapping must use declared source and target values"
        )

    mappings: list[EnumValueCandidate] = []
    for external in source:
        if external in explicit:
            mappings.append(
                EnumValueCandidate(
                    external_value=external,
                    canonical_value=explicit[external],
                    score=1.0,
                    status=EnumMappingStatus.CONFIRMED,
                    evidence=(
                        "Explicit mapping supplied by caller configuration or documentation.",
                    ),
                )
            )
            continue
        scored: list[tuple[str, float, str]] = []
        for canonical in target:
            match = _similarity(external, canonical)
            description_score = _description_similarity(
                source_descriptions.get(external, ""), target_descriptions.get(canonical, "")
            )
            if match is not None:
                score, reason = match
                if description_score:
                    score = min(1.0, score * 0.8 + description_score * 0.2)
                    reason += " Descriptions provide additional support."
                scored.append((canonical, score, reason))
            elif description_score >= 0.5:
                scored.append(
                    (canonical, description_score * 0.7, "Descriptions provide partial support.")
                )
        scored.sort(key=lambda item: (-item[1], item[0]))
        if not scored:
            mappings.append(
                EnumValueCandidate(
                    external_value=external,
                    score=0.0,
                    status=EnumMappingStatus.UNKNOWN,
                    evidence=("No conservative evidence identifies a canonical value.",),
                )
            )
            continue
        best = scored[0]
        alternatives = tuple(item[0] for item in scored[1:])
        evidence: tuple[str, ...]
        if len(scored) > 1 and best[1] - scored[1][1] < 0.1:
            status = EnumMappingStatus.CONFLICTING
            evidence = (best[2], "Competing canonical values have similar support.")
        elif best[1] >= 0.9:
            status = EnumMappingStatus.HIGH_CONFIDENCE
            evidence = (best[2],)
        else:
            status = EnumMappingStatus.REVIEW_REQUIRED
            evidence = (best[2], "Evidence is insufficient for automatic enum translation.")
        mappings.append(
            EnumValueCandidate(
                external_value=external,
                canonical_value=best[0],
                score=best[1],
                status=status,
                evidence=evidence,
                alternatives=alternatives,
            )
        )

    observed = _as_values(observed_values, "observed_values") if observed_values else ()
    unseen = tuple(value for value in observed if value not in source)
    return EnumMappingResult(
        external_values=source,
        canonical_values=target,
        mappings=tuple(mappings),
        unseen_values=unseen,
    )


def translate_enum(result: EnumMappingResult, value: str | int) -> str:
    """Translate only a declared, approved-enough value.

    Unknown or unseen values fail loudly. Review-required and conflicting
    hypotheses also fail until a human supplies an explicit mapping.
    """
    external = str(value)
    if external in result.unseen_values or external not in result.external_values:
        raise UnknownEnumValueError(f"unseen enum value: {external}")
    candidate = result.candidate(external)
    if candidate is None or candidate.canonical_value is None:
        raise UnknownEnumValueError(f"unmapped enum value: {external}")
    if candidate.status not in (EnumMappingStatus.HIGH_CONFIDENCE, EnumMappingStatus.CONFIRMED):
        raise UnapprovedEnumMappingError(
            f"enum value {external} requires review ({candidate.status.value})"
        )
    return candidate.canonical_value
