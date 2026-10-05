"""Inspectable, deterministic mapping signals with fixed policy weights.

Weights are name .45, description .25, type .15, and value profile .15.
They are baseline policy choices, not learned probabilities or calibration.
Unavailable evidence has ``score=None`` and is excluded from the weighted mean.
The vocabulary below normalizes individual reusable terms, never whole source
paths. Similarity is lexical overlap; it does not claim semantic understanding.
"""

from __future__ import annotations

import re
from math import sqrt

from crosswalk_discovery import ExternalField, FieldType
from crosswalk_profiler import FieldProfile, ObservedType, SemanticType

from .models import CanonicalField, MappingEvidence, SignalEvidence

_CAMEL_BOUNDARY = re.compile(r"([a-z0-9])([A-Z])")
_ACRONYM_BOUNDARY = re.compile(r"([A-Z]+)([A-Z][a-z])")
_WORDS = re.compile(r"[a-z0-9]+")
_ALIASES: dict[str, tuple[str, ...]] = {
    "clm": ("claim",),
    "claims": ("claim",),
    "identifier": ("id",),
    "identifiers": ("id",),
    "reference": ("id",),
    "ref": ("id",),
    "number": ("id",),
    "num": ("id",),
    "no": ("id",),
    "dt": ("date",),
    "dates": ("date",),
    "given": ("first",),
    "forename": ("first", "name"),
    "surname": ("last", "name"),
    "family": ("last",),
    "names": ("name",),
    "nm": ("name",),
    "party": ("person",),
    "cd": ("code",),
    "amt": ("amount",),
    "amounts": ("amount",),
    "pmt": ("payment",),
    "pmts": ("payment",),
    "payments": ("payment",),
    "paid": ("payment",),
    "pd": ("payment",),
    "pay": ("payment",),
    "rsrv": ("reserve",),
    "rsv": ("reserve",),
    "reserves": ("reserve",),
    "inc": ("incurred",),
    "expiry": ("expiration",),
    "expires": ("expiration",),
    "exp": ("expiration",),
    "eff": ("effective",),
    "insureds": ("insured",),
    "claimants": ("claimant",),
    "policies": ("policy",),
    "pol": ("policy",),
}
_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "if",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "under",
        "with",
    }
)
_WRAPPERS = frozenset({"data", "item", "items", "result", "results", "response", "records"})
_ROLES = frozenset({"claimant", "insured"})
_ID_GENERIC = frozenset({"id", "code", "external", "unique", "stable", "reference", "ref"})


def normalized_tokens(text: str) -> frozenset[str]:
    """Split camel/snake/acronym words and expand conservative term aliases."""
    expanded = _CAMEL_BOUNDARY.sub(r"\1 \2", _ACRONYM_BOUNDARY.sub(r"\1 \2", text))
    return frozenset(
        token
        for word in _WORDS.findall(expanded.lower())
        for token in _ALIASES.get(word, (word,))
        if token not in _STOP_WORDS
    )


def _overlap(left: frozenset[str], right: frozenset[str]) -> float:
    """Binary cosine overlap: identical token sets score one, disjoint zero."""
    if not left or not right:
        return 0.0
    return len(left & right) / sqrt(len(left) * len(right))


def _identifier_subject(field: ExternalField) -> frozenset[str]:
    # An explicit invoiceId remains an invoice id inside a claim object. A bare
    # id can borrow its nearest object's name, but not an unrelated ancestor.
    leaf_subject = normalized_tokens(field.name) - _ID_GENERIC
    if leaf_subject:
        return leaf_subject
    for parent in reversed(field.json_path.split(".")[:-1]):
        subject = normalized_tokens(parent) - _WRAPPERS - _ID_GENERIC
        if subject:
            return subject
    return frozenset()


def _name(field: ExternalField, target: CanonicalField) -> SignalEvidence:
    source_leaf = normalized_tokens(field.name)
    target_leaf = normalized_tokens(target.name)
    source_path = normalized_tokens(field.json_path) - _WRAPPERS
    # The canonical root is a container, not evidence that every field is a claim id.
    target_path = normalized_tokens(target.path.partition(".")[2])
    source_roles = (source_path | source_leaf) & _ROLES
    target_roles = target_path & _ROLES
    if source_roles and target_roles and source_roles.isdisjoint(target_roles):
        return SignalEvidence(score=0.0, weight=0.45, reason="Explicit person roles conflict.")

    # Include role/entity context without penalizing common response wrappers.
    contextual = _overlap(source_path, target_path)
    lexical = _overlap(source_leaf, target_leaf)
    score = max(contextual, lexical)
    constraints: list[str] = []
    if target_roles and not source_roles:
        score *= 0.65
        constraints.append("source does not identify the required person role")
    if "id" in target_leaf:
        source_subject = _identifier_subject(field)
        target_subject = target_path - _ID_GENERIC
        if not (source_subject & target_subject):
            score = min(score, 0.35)
            constraints.append("shared identifier syntax does not identify its entity")
    matched = ", ".join(sorted((source_path | source_leaf) & target_path)) or "none"
    reason = f"Normalized name/path token overlap; shared terms: {matched}."
    if constraints:
        reason += " " + "; ".join(constraints) + "."
    return SignalEvidence(score=score, weight=0.45, reason=reason)


def _description(field: ExternalField, target: CanonicalField) -> SignalEvidence:
    source = normalized_tokens(field.description or "")
    destination = normalized_tokens(target.description)
    if not source or not destination:
        return SignalEvidence(score=None, weight=0.25, reason="Description evidence unavailable.")
    source_roles = source & _ROLES
    target_roles = normalized_tokens(target.path) & _ROLES
    if source_roles and target_roles and source_roles.isdisjoint(target_roles):
        return SignalEvidence(
            score=0.0, weight=0.25, reason="Description names a conflicting role."
        )
    shared_count = len(source & destination)
    return SignalEvidence(
        score=_overlap(source, destination),
        weight=0.25,
        reason=f"Normalized description token overlap ({shared_count} shared terms).",
    )


def _compatible(source: FieldType, target: FieldType) -> bool:
    # Integer-to-number is lossless; number-to-integer requires validation.
    return source == target or (source is FieldType.INTEGER and target is FieldType.NUMBER)


def _type(field: ExternalField, target: CanonicalField) -> SignalEvidence:
    declared = {field.data_type, *field.extra_types} - {FieldType.NULL, FieldType.UNKNOWN}
    if not declared or target.data_type is FieldType.UNKNOWN:
        return SignalEvidence(score=None, weight=0.15, reason="Declared type evidence unavailable.")
    count = sum(_compatible(kind, target.data_type) for kind in declared)
    source_names = ", ".join(sorted(kind.value for kind in declared))
    return SignalEvidence(
        score=count / len(declared),
        weight=0.15,
        reason=f"{count}/{len(declared)} declared types ({source_names}) are compatible with "
        f"{target.data_type.value}; integer-to-number widening is allowed.",
    )


def _profile(profile: FieldProfile | None, target: CanonicalField) -> SignalEvidence:
    if profile is None or profile.present_count <= profile.null_count:
        return SignalEvidence(score=None, weight=0.15, reason="No non-null profile evidence.")
    observed = set(profile.observed_types) - {ObservedType.NULL}
    if not observed:
        return SignalEvidence(score=None, weight=0.15, reason="Observed type evidence unavailable.")
    compatible_fraction = sum(
        _compatible(FieldType(kind.value), target.data_type) for kind in observed
    ) / len(observed)
    observed_semantic = profile.semantic_type
    target_semantic = target.semantic_type
    if observed_semantic is SemanticType.UNKNOWN or target_semantic is SemanticType.UNKNOWN:
        support = 0.5
        detail = "no discriminating semantic hint"
    elif observed_semantic is target_semantic:
        support = 0.75
        detail = f"matching {observed_semantic.value} heuristic"
    elif {observed_semantic, target_semantic} <= {SemanticType.NUMBER, SemanticType.CURRENCY}:
        support = 0.5
        detail = "numeric heuristic does not establish a financial meaning"
    else:
        support = 0.2
        detail = f"{observed_semantic.value} heuristic differs from {target_semantic.value}"
    return SignalEvidence(
        score=compatible_fraction * support,
        weight=0.15,
        reason=f"Observed type compatibility {compatible_fraction:.2f}; {detail}. "
        "Value patterns are weak support, not proof of business meaning.",
    )


def score_field(
    field: ExternalField, target: CanonicalField, profile: FieldProfile | None = None
) -> MappingEvidence:
    """Score one pair without ground truth, raw sample output, or model calls.

    Profiles must describe the source path. A mismatched profile is a caller
    error; silently using it would fabricate evidence for another field.
    """
    if profile is not None and profile.json_path != field.json_path:
        raise ValueError("Profile path does not match the external field path")
    return MappingEvidence(
        name=_name(field, target),
        description=_description(field, target),
        type=_type(field, target),
        value_profile=_profile(profile, target),
    )
