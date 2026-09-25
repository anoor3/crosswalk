"""Extract the observed values at a ``json_path`` from a payload.

The profiler needs, for each field discovered by the OpenAPI analyzer, the set
of concrete values that field takes across sample payloads. This module walks a
payload following the exact ``json_path`` grammar the discovery flattener
produces:

* ``$``                      -> the whole payload
* ``$.a.b``                  -> nested object access
* ``$.arr[*]``               -> every element of an array (fan-out)
* ``$.arr[*].field``         -> ``field`` of every array element

Robustness (CHECKER §15: "missing fields crash the system" is a failure):
a path segment that does not exist yields an *absent* result rather than an
error, and a ``[*]`` over a non-list yields nothing. Explicit JSON ``null`` is
distinguished from absence — both matter to a profile (null rate vs. presence).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExtractedValue:
    """One value produced by resolving a json_path.

    ``present`` is False when the path did not exist in the payload at all.
    When ``present`` is True, ``value`` is the concrete value found, which may
    itself be ``None`` (an explicit JSON null).
    """

    present: bool
    value: Any = None

    @classmethod
    def absent(cls) -> ExtractedValue:
        return cls(present=False, value=None)

    @classmethod
    def of(cls, value: Any) -> ExtractedValue:
        return cls(present=True, value=value)


def _parse_segments(json_path: str) -> list[str]:
    """Split a json_path into ordered segments.

    ``$.arr[*].field`` -> ``["arr", "[*]", "field"]``. The leading ``$`` is
    dropped. Bracket groups become their own segments.
    """
    body = json_path.lstrip("$")
    segments: list[str] = []
    buf: list[str] = []
    i = 0
    while i < len(body):
        char = body[i]
        if char == ".":
            if buf:
                segments.append("".join(buf))
                buf = []
        elif char == "[":
            if buf:
                segments.append("".join(buf))
                buf = []
            # Consume up to and including the closing bracket.
            close = body.find("]", i)
            if close == -1:
                buf.append(body[i:])
                i = len(body)
                continue
            segments.append(body[i : close + 1])
            i = close + 1
            continue
        else:
            buf.append(char)
        i += 1
    if buf:
        segments.append("".join(buf))
    return segments


def extract_values(payload: Any, json_path: str) -> list[ExtractedValue]:
    """Resolve ``json_path`` against ``payload``, returning all matched values.

    A path without ``[*]`` yields at most one result. A path with one or more
    ``[*]`` fans out and may yield many (one per array element combination).
    A path that cannot be resolved yields a single :meth:`ExtractedValue.absent`
    so callers can count absence without special-casing exceptions.
    """
    segments = _parse_segments(json_path)
    return _walk(payload, segments)


def _walk(node: Any, segments: list[str]) -> list[ExtractedValue]:
    # Base case: no more segments -> the current node is a value.
    if not segments:
        return [ExtractedValue.of(node)]

    head, rest = segments[0], segments[1:]

    if head == "[*]":
        if not isinstance(node, list):
            return [ExtractedValue.absent()]
        results: list[ExtractedValue] = []
        for element in node:
            results.extend(_walk(element, rest))
        # An empty array contributes no observations (not "absent").
        return results

    # Object key access.
    if isinstance(node, dict):
        if head not in node:
            return [ExtractedValue.absent()]
        return _walk(node[head], rest)

    # We expected an object here but found something else (or None).
    return [ExtractedValue.absent()]
