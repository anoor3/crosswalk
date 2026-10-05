"""Pure, deterministic ranking and conservative routing for human review."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from crosswalk_discovery import ExternalField, FieldType
from crosswalk_profiler import FieldProfile, ObservedType, SemanticType

from .models import CanonicalField, MappingAlternative, MappingCandidate, MappingStatus
from .signals import normalized_tokens, score_field
from .targets import canonical_fields

# These are versioned heuristic policy thresholds, not fitted probabilities.
MIN_SEMANTIC_SUPPORT = 0.25
HIGH_SCORE = 0.75
HIGH_SEMANTIC_SUPPORT = 0.75
MIN_MARGIN = 0.15
_SOURCE_WRAPPERS = frozenset({"data", "item", "items", "result", "results", "response", "records"})


def _unique(values: Sequence[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label} paths")


def map_fields(
    fields: Sequence[ExternalField],
    profiles: Sequence[FieldProfile] | Mapping[str, FieldProfile] = (),
    targets: Sequence[CanonicalField] | None = None,
) -> tuple[MappingCandidate, ...]:
    """Rank scalar targets for one endpoint's fields, preserving every input.

    Inputs must describe a single endpoint/schema: paths identify fields only
    within that scope. Profiles are optional; supplied profiles must match an
    input field. No I/O, sample logging, ground truth, model calls, or approval.
    Results retain input order; ties break by canonical path for stable output.
    """
    target_fields = tuple(canonical_fields() if targets is None else targets)
    _unique([field.json_path for field in fields], "external field")
    _unique([target.path for target in target_fields], "canonical field")
    if isinstance(profiles, Mapping):
        if any(key != profile.json_path for key, profile in profiles.items()):
            raise ValueError("profile dictionary keys must match profile json_path")
        profile_values = tuple(profiles.values())
    else:
        profile_values = tuple(profiles)
    _unique([profile.json_path for profile in profile_values], "profile")
    by_path = {profile.json_path: profile for profile in profile_values}
    if set(by_path) - {field.json_path for field in fields}:
        raise ValueError("profiles must refer to supplied external fields")

    candidates = tuple(
        _map_field(
            field,
            by_path.get(field.json_path),
            target_fields,
            _has_optional_ancestor(field.json_path, fields),
        )
        for field in fields
    )
    # Two competing source fields must not both look safe for a single target.
    # Preserve both hypotheses and their evidence instead of selecting a winner.
    selected: dict[str, list[MappingCandidate]] = {}
    for candidate in candidates:
        if candidate.canonical_path is not None:
            selected.setdefault(candidate.canonical_path, []).append(candidate)
    collisions = {path for path, choices in selected.items() if len(choices) > 1}
    return tuple(
        candidate.model_copy(
            update={
                "status": MappingStatus.REVIEW_REQUIRED,
                "reasons": (*candidate.reasons, "Multiple source fields compete for this target."),
            }
        )
        if candidate.canonical_path in collisions
        and candidate.status == MappingStatus.HIGH_CONFIDENCE
        else candidate
        for candidate in candidates
    )


def _map_field(
    field: ExternalField,
    profile: FieldProfile | None,
    targets: tuple[CanonicalField, ...],
    optional_ancestor: bool,
) -> MappingCandidate:
    if field.data_type in (FieldType.OBJECT, FieldType.ARRAY) or not targets:
        return MappingCandidate(
            external_path=field.json_path,
            canonical_path=None,
            score=0,
            status=MappingStatus.UNRESOLVED,
            evidence=None,
            reasons=("Container fields are not scalar mappings." if targets else "No targets.",),
        )
    rankings = []
    for target in targets:
        evidence = score_field(field, target, profile)
        rankings.append(
            MappingAlternative(canonical_path=target.path, score=evidence.score, evidence=evidence)
        )
    rankings.sort(key=lambda choice: (-choice.score, choice.canonical_path))
    best = rankings[0]
    target = next(target for target in targets if target.path == best.canonical_path)
    semantic_support = max(best.evidence.name.score or 0, best.evidence.description.score or 0)
    margin = best.score - rankings[1].score if len(rankings) > 1 else best.score
    reasons: list[str] = []

    name_order = sorted(rankings, key=lambda item: -(item.evidence.name.score or 0))
    description_order = sorted(rankings, key=lambda item: -(item.evidence.description.score or 0))
    # Only independent, clearly separated lexical signals can establish this
    # conflict; weak description overlap must not manufacture disagreement.
    semantic_conflict = (
        len(rankings) > 1
        and (name_order[0].evidence.name.score or 0) >= HIGH_SEMANTIC_SUPPORT
        and (description_order[0].evidence.description.score or 0) >= 0.6
        and (name_order[0].evidence.name.score or 0) - (name_order[1].evidence.name.score or 0)
        >= MIN_MARGIN
        and (description_order[0].evidence.description.score or 0)
        - (description_order[1].evidence.description.score or 0)
        >= MIN_MARGIN
        and name_order[0].canonical_path != description_order[0].canonical_path
    )
    observed_types = set(profile.observed_types) - {ObservedType.NULL} if profile else set()
    expected_types = {target.data_type.value}
    if target.data_type == FieldType.NUMBER:
        expected_types.add(FieldType.INTEGER.value)
    observed_conflict = bool(observed_types) and any(
        observed.value not in expected_types for observed in observed_types
    )
    # Capped examples can disprove a vocabulary, never prove full conformance.
    enum_counterexample = bool(
        profile
        and target.enum_values
        and any(value not in target.enum_values for value in profile.sample_values)
    )

    if semantic_support < MIN_SEMANTIC_SUPPORT:
        status = MappingStatus.UNRESOLVED
        reasons.append(
            "Names and descriptions do not identify a target; types alone are insufficient."
        )
    elif best.evidence.type.score == 0:
        status = MappingStatus.CONFLICTING
        reasons.append("The leading semantic hypothesis conflicts with the declared type.")
    elif profile is not None and profile.is_mixed_type:
        status = MappingStatus.CONFLICTING
        reasons.append("Mixed observed types require inspection before mapping.")
    elif observed_conflict:
        status = MappingStatus.CONFLICTING
        reasons.append("Observed values conflict with the proposed target's type.")
    elif semantic_conflict:
        status = MappingStatus.CONFLICTING
        reasons.append("Names and descriptions strongly support different targets.")
    elif enum_counterexample:
        status = MappingStatus.CONFLICTING
        reasons.append("Observed enum examples include a value outside the target vocabulary.")
    else:
        if best.score < HIGH_SCORE or semantic_support < HIGH_SEMANTIC_SUPPORT:
            reasons.append("Semantic support is below the high-confidence threshold.")
        if margin < MIN_MARGIN:
            reasons.append("Competing targets have similar scores.")
        unmatched = (
            (normalized_tokens(field.name) | normalized_tokens(field.json_path))
            - normalized_tokens(target.path)
            - _SOURCE_WRAPPERS
        )
        if unmatched:
            reasons.append("Source name or context includes terms absent from the proposed target.")
        if (best.evidence.description.score or 0) >= MIN_SEMANTIC_SUPPORT and any(
            item.canonical_path != best.canonical_path
            and (item.evidence.description.score or 0) >= MIN_SEMANTIC_SUPPORT
            and (best.evidence.description.score or 0) - (item.evidence.description.score or 0)
            < MIN_MARGIN
            for item in rankings
        ):
            reasons.append("Description evidence leaves competing targets.")
        if re.search(
            r"\b(not|never|exclude|excludes|excluding|unrelated)\b", field.description or "", re.I
        ):
            reasons.append("Description contains caution terms that require human interpretation.")
        if field.is_array_item or "[*]" in field.json_path:
            reasons.append("Array members require a selection or aggregation rule.")
        if target.semantic_type == SemanticType.CURRENCY:
            reasons.append(
                "Financial meaning requires domain validation; numeric values cannot prove it."
            )
        if field.extra_types or field.data_type in (FieldType.UNKNOWN, FieldType.NULL):
            reasons.append("The declared type is uncertain or has multiple alternatives.")
        if best.evidence.type.score is None or best.evidence.type.score < 1:
            reasons.append("Type conversion or additional type validation is required.")
        if target.enum_values and not (
            field.enum_values and set(field.enum_values) <= set(target.enum_values)
        ):
            reasons.append("Enum code translation or validation is required.")
        if not target.nullable and (
            not field.required
            or field.nullable
            or optional_ancestor
            or (
                profile is not None
                and (profile.null_count > 0 or profile.present_count < profile.sample_count)
            )
        ):
            reasons.append("Nullable or absent source values need a policy for a non-null target.")
        if profile is not None and profile.present_count <= profile.null_count:
            reasons.append("No non-null observations support this mapping.")
        if (
            profile is not None
            and profile.present_count > profile.null_count
            and target.semantic_type == SemanticType.DATE
            and profile.semantic_type != SemanticType.DATE
        ):
            reasons.append("Observed strings have no recognized date format for this date target.")
        status = MappingStatus.REVIEW_REQUIRED if reasons else MappingStatus.HIGH_CONFIDENCE
        if not reasons:
            reasons.append("Strong semantic support, compatible type, and a clear ranking margin.")

    unresolved = status == MappingStatus.UNRESOLVED
    return MappingCandidate(
        external_path=field.json_path,
        canonical_path=None if unresolved else best.canonical_path,
        score=best.score,
        status=status,
        evidence=best.evidence,
        alternatives=tuple(rankings if unresolved else rankings[1:]),
        reasons=tuple(reasons),
    )


def _has_optional_ancestor(path: str, fields: Sequence[ExternalField]) -> bool:
    """Propagate object presence risk to nested leaves.

    OpenAPI's ``required`` flag is local to its enclosing object. A required
    child under an optional or nullable parent can still be absent, so mapping
    it into a non-null canonical field needs an explicit absence policy.
    """
    known = {field.json_path: field for field in fields}
    current = path
    while "." in current:
        current = current.rsplit(".", 1)[0]
        parent = known.get(current)
        if parent is not None and (not parent.required or parent.nullable):
            return True
    return False
