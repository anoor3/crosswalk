from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DriftKind(StrEnum):
    ADDED_FIELD = "ADDED_FIELD"
    REMOVED_FIELD = "REMOVED_FIELD"
    TYPE_CHANGED = "TYPE_CHANGED"
    ENUM_CHANGED = "ENUM_CHANGED"


class DriftEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: DriftKind
    path: str = Field(min_length=1)
    before: object | None = None
    after: object | None = None


def schema_fingerprint(schema: dict[str, Any]) -> str:
    canonical = json.dumps(schema, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def detect_drift(before: dict[str, Any], after: dict[str, Any]) -> tuple[DriftEvent, ...]:
    before_props = before.get("properties", {})
    after_props = after.get("properties", {})
    events: list[DriftEvent] = []
    for path in sorted(set(before_props) | set(after_props)):
        if path not in before_props:
            events.append(
                DriftEvent(kind=DriftKind.ADDED_FIELD, path=path, after=after_props[path])
            )
        elif path not in after_props:
            events.append(
                DriftEvent(kind=DriftKind.REMOVED_FIELD, path=path, before=before_props[path])
            )
        else:
            old, new = before_props[path], after_props[path]
            if old.get("type") != new.get("type"):
                events.append(
                    DriftEvent(
                        kind=DriftKind.TYPE_CHANGED,
                        path=path,
                        before=old.get("type"),
                        after=new.get("type"),
                    )
                )
            if old.get("enum") != new.get("enum"):
                events.append(
                    DriftEvent(
                        kind=DriftKind.ENUM_CHANGED,
                        path=path,
                        before=old.get("enum"),
                        after=new.get("enum"),
                    )
                )
    return tuple(events)
