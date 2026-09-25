"""The deterministic value-profiling engine.

Given the values a field takes across sample payloads, compute a
:class:`FieldProfile`: counts, null/unique rates, per-type statistics, a coarse
string pattern, a detected date format, and a heuristic semantic type. Every
step is mechanical — no LLM, no randomness (PLANNER §16, CHECKER §15).

The heuristics (identifier / date / currency / enum-candidate) are intentionally
simple and explainable; they are *hints* for the mapping phase, and the raw
statistics that justify each hint travel with it on the profile.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Any

from .extract import ExtractedValue, extract_values
from .profile import (
    FieldProfile,
    NumericStats,
    ObservedType,
    SemanticType,
    StringStats,
)

# Cap on how many example values a profile retains (privacy + size — CHECKER §15).
_MAX_SAMPLE_VALUES = 10

# Date formats we attempt, ordered from most to least specific/common. If every
# non-null string value parses under one of these, the field is a date.
_DATE_FORMATS: tuple[str, ...] = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%d/%m/%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
)

# Enum-candidate thresholds: few distinct values, repeated often, enough samples.
_ENUM_MAX_UNIQUE = 12
_ENUM_MAX_UNIQUE_RATE = 0.5
_ENUM_MIN_SAMPLES = 4

# Identifier threshold: nearly every value distinct.
_IDENTIFIER_MIN_UNIQUE_RATE = 0.9


def _observed_type(value: Any) -> ObservedType:
    """Map a Python/JSON value to its ObservedType.

    ``bool`` is checked before ``int`` because ``bool`` is a subclass of ``int``
    in Python — otherwise ``True`` would be miscounted as an integer.
    """
    if isinstance(value, bool):
        return ObservedType.BOOLEAN
    if isinstance(value, int):
        return ObservedType.INTEGER
    if isinstance(value, float):
        return ObservedType.NUMBER
    if isinstance(value, str):
        return ObservedType.STRING
    if isinstance(value, dict):
        return ObservedType.OBJECT
    if isinstance(value, list):
        return ObservedType.ARRAY
    return ObservedType.NULL


def _string_signature(value: str) -> str:
    """A coarse structural signature: A=alpha, 0=digit, other chars kept.

    'CLM-88291' -> 'AAA-00000'. Used to detect a dominant shape.
    """
    out: list[str] = []
    for char in value:
        if char.isalpha():
            out.append("A")
        elif char.isdigit():
            out.append("0")
        else:
            out.append(char)
    return "".join(out)


def _try_date_format(strings: Sequence[str]) -> str | None:
    """Return a date format under which ALL strings parse, or None."""
    if not strings:
        return None
    for fmt in _DATE_FORMATS:
        if all(_parses(s, fmt) for s in strings):
            return fmt
    return None


def _parses(value: str, fmt: str) -> bool:
    try:
        datetime.strptime(value, fmt)
    except (ValueError, TypeError):
        return False
    return True


def _looks_like_currency(numbers: Sequence[float], strings: Sequence[str]) -> bool:
    """Heuristic: numeric values that look monetary.

    We treat a numeric field as currency-like when its string renderings carry
    exactly two decimal places (cents) for a majority of values, OR the numeric
    values are non-negative with a plausible money magnitude and appear as
    decimals. Deliberately conservative: currency is only a *hint*.
    """
    if strings:
        two_dp = sum(1 for s in strings if _has_two_decimals(s))
        if two_dp and two_dp >= len(strings) / 2:
            return True
    if numbers:
        # All non-negative and at least one fractional -> plausibly money.
        return all(n >= 0 for n in numbers) and any(n != int(n) for n in numbers)
    return False


def _has_two_decimals(value: str) -> bool:
    if "." not in value:
        return False
    decimals = value.rsplit(".", 1)[-1]
    return len(decimals) == 2 and decimals.isdigit()


def profile_values(json_path: str, extracted: Iterable[ExtractedValue]) -> FieldProfile:
    """Compute a FieldProfile from the extracted occurrences of a field."""
    items = list(extracted)
    sample_count = len(items)
    present = [e.value for e in items if e.present]
    present_count = len(present)
    non_null = [v for v in present if v is not None]
    null_count = present_count - len(non_null)

    null_rate = (null_count / sample_count) if sample_count else 0.0

    # Distinct non-null values (stringified for a stable, hashable key).
    distinct = {_stable_key(v) for v in non_null}
    unique_count = len(distinct)
    unique_rate = (unique_count / len(non_null)) if non_null else 0.0

    observed = {_observed_type(v) for v in non_null}
    is_mixed_type = len(observed) > 1

    # Per-type stats.
    numbers = [
        float(v) for v in non_null if isinstance(v, (int, float)) and not isinstance(v, bool)
    ]
    strings = [v for v in non_null if isinstance(v, str)]
    numeric_stats = _numeric_stats(numbers)
    string_stats = _string_stats(strings)

    # Capped, stringified sample of distinct values for inspection.
    sample_values = _capped_samples(non_null)

    detected_pattern = _dominant_pattern(strings)
    detected_date_format = _try_date_format(strings) if strings else None

    semantic_type = _infer_semantic_type(
        observed=observed,
        non_null=non_null,
        numbers=numbers,
        strings=strings,
        unique_count=unique_count,
        unique_rate=unique_rate,
        sample_count=present_count,
        detected_pattern=detected_pattern,
        detected_date_format=detected_date_format,
    )

    return FieldProfile(
        json_path=json_path,
        sample_count=sample_count,
        present_count=present_count,
        null_count=null_count,
        null_rate=null_rate,
        unique_count=unique_count,
        unique_rate=unique_rate,
        observed_types=tuple(sorted(observed, key=lambda t: t.value)),
        is_mixed_type=is_mixed_type,
        numeric_stats=numeric_stats,
        string_stats=string_stats,
        sample_values=sample_values,
        detected_pattern=detected_pattern,
        detected_date_format=detected_date_format,
        semantic_type=semantic_type,
    )


def profile_field(payloads: Iterable[Any], json_path: str) -> FieldProfile:
    """Profile one field across many sample payloads."""
    extracted: list[ExtractedValue] = []
    for payload in payloads:
        extracted.extend(extract_values(payload, json_path))
    return profile_values(json_path, extracted)


def profile_fields(payloads: Sequence[Any], json_paths: Iterable[str]) -> dict[str, FieldProfile]:
    """Profile many fields across the same set of payloads.

    Returns a mapping of json_path -> FieldProfile. Object/array container
    paths can be included; their profiles simply describe container occurrences.
    """
    return {path: profile_field(payloads, path) for path in json_paths}


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def _stable_key(value: Any) -> str:
    """A stable, hashable string key for a value (for uniqueness counting)."""
    return f"{type(value).__name__}:{value!r}"


def _numeric_stats(numbers: Sequence[float]) -> NumericStats | None:
    if not numbers:
        return None
    return NumericStats(
        minimum=min(numbers),
        maximum=max(numbers),
        mean=sum(numbers) / len(numbers),
    )


def _string_stats(strings: Sequence[str]) -> StringStats | None:
    if not strings:
        return None
    lengths = [len(s) for s in strings]
    return StringStats(
        min_length=min(lengths),
        max_length=max(lengths),
        mean_length=sum(lengths) / len(lengths),
    )


def _capped_samples(non_null: Sequence[Any]) -> tuple[str, ...]:
    """First N distinct values, stringified, preserving first-seen order."""
    seen: dict[str, None] = {}
    for value in non_null:
        key = str(value)
        if key not in seen:
            seen[key] = None
        if len(seen) >= _MAX_SAMPLE_VALUES:
            break
    return tuple(seen.keys())


def _dominant_pattern(strings: Sequence[str]) -> str | None:
    """Return the most common structural signature if it dominates (>= 60%)."""
    if not strings:
        return None
    signatures = Counter(_string_signature(s) for s in strings)
    top_sig, top_count = signatures.most_common(1)[0]
    if top_count >= len(strings) * 0.6:
        return top_sig
    return None


def _infer_semantic_type(
    *,
    observed: set[ObservedType],
    non_null: Sequence[Any],
    numbers: Sequence[float],
    strings: Sequence[str],
    unique_count: int,
    unique_rate: float,
    sample_count: int,
    detected_pattern: str | None,
    detected_date_format: str | None,
) -> SemanticType:
    """Deterministic semantic-type heuristic over the computed stats."""
    if not non_null:
        return SemanticType.UNKNOWN

    # Booleans first (bool is an int subclass).
    if observed == {ObservedType.BOOLEAN}:
        return SemanticType.BOOLEAN

    # Dates: every string value parsed under a single format.
    if detected_date_format is not None and strings:
        return SemanticType.DATE

    # Currency (money-like) is checked before enum so a low-cardinality money
    # field isn't misread as an enum. Applies to numeric and decimal-string.
    if numbers and not strings and _looks_like_currency(numbers, ()):
        return SemanticType.CURRENCY
    if strings and not numbers and _looks_like_currency((), strings):
        return SemanticType.CURRENCY

    # Enum candidate: few distinct values, repeated, enough samples. Applies to
    # both coded strings and small integer code sets.
    if (
        sample_count >= _ENUM_MIN_SAMPLES
        and unique_count <= _ENUM_MAX_UNIQUE
        and unique_rate <= _ENUM_MAX_UNIQUE_RATE
    ):
        return SemanticType.ENUM_CANDIDATE

    # Numeric fields (non-currency).
    if numbers and not strings:
        return SemanticType.NUMBER

    # String fields (non-currency).
    if strings and not numbers:
        # Identifier: highly unique + a dominant pattern that includes digits.
        if (
            unique_rate >= _IDENTIFIER_MIN_UNIQUE_RATE
            and detected_pattern is not None
            and "0" in detected_pattern
        ):
            return SemanticType.IDENTIFIER
        return SemanticType.FREE_TEXT

    return SemanticType.UNKNOWN
