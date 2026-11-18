"""Sample-to-target mapping and explicit, bounded conversion plans."""

import inspect
import json
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from crosswalk_discovery import ExternalField, FieldType
from crosswalk_mapping import CanonicalField, MappingStatus, map_fields
from crosswalk_profiler import profile_fields

from . import conversion_runtime

router = APIRouter(prefix="/workbench/conversion")
Operation = Literal[
    "copy",
    "text",
    "number",
    "integer",
    "cents_to_dollars",
    "date_iso",
    "date_us",
    "date_day_first",
    "omit",
]


def fields(record: dict[str, Any], prefix: str = "", depth: int = 0) -> dict[str, Any]:
    if depth > 12:
        raise ValueError("Objects may be nested at most 12 levels deep")
    result: dict[str, Any] = {}
    for key, value in record.items():
        path = prefix + "/" + key.replace("~", "~0").replace("/", "~1")
        if isinstance(value, dict) and value:
            result.update(fields(value, path, depth + 1))
        else:
            result[path] = value
        if len(result) > 100:
            raise ValueError("Use at most 100 fields per record")
    return result


def _json_path(pointer: str) -> str:
    tokens = pointer.split("/")[1:]
    return "$." + ".".join(token.replace("~1", "/").replace("~0", "~") for token in tokens)


def _field_type(value: Any) -> FieldType:
    return {
        "null": FieldType.NULL,
        "boolean": FieldType.BOOLEAN,
        "number": FieldType.NUMBER,
        "string": FieldType.STRING,
        "array": FieldType.ARRAY,
        "object": FieldType.OBJECT,
    }[conversion_runtime.value_type(value)]


def _source_fields(records: list[dict[str, Any]]) -> tuple[ExternalField, ...]:
    values: dict[str, Any] = {}
    presence: dict[str, int] = {}
    for record in records:
        flattened = fields(record)
        for path, value in flattened.items():
            if path not in values or values[path] is None:
                values[path] = value
            presence[path] = presence.get(path, 0) + 1
    return tuple(
        ExternalField(
            json_path=_json_path(path),
            name=path.rsplit("/", 1)[-1].replace("~1", "/").replace("~0", "~"),
            data_type=_field_type(value),
            required=presence[path] == len(records),
        )
        for path, value in values.items()
    )


def _target_fields(target: dict[str, Any]) -> tuple[CanonicalField, ...]:
    return tuple(
        CanonicalField(
            path=path,
            name=path.rsplit("/", 1)[-1].replace("~1", "/").replace("~0", "~"),
            data_type=_field_type(value),
        )
        for path, value in fields(target).items()
    )


class Samples(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    records: list[dict[str, Any]] = Field(min_length=1, max_length=200)
    target: dict[str, Any]

    @model_validator(mode="after")
    def bounded(self) -> "Samples":
        try:
            encoded = json.dumps([self.records, self.target], allow_nan=False)
            if len(encoded.encode()) > 800_000:
                raise ValueError("Use at most 800 KB of sample data")
            for record in [*self.records, self.target]:
                conversion_runtime.validate_json(record)
                fields(record)
            if len({path for record in self.records for path in fields(record)}) > 100:
                raise ValueError("Use at most 100 distinct source fields")
            if not self.target:
                raise ValueError("Provide a non-empty target example")
            if any(value is None for value in fields(self.target).values()):
                raise ValueError("Target examples need non-null values to establish field types")
        except (RecursionError, OverflowError) as error:
            raise ValueError("Sample data is too deeply nested") from error
        return self


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source: str = Field(max_length=1000)
    target: str = Field(max_length=1000)
    operation: Operation = "copy"
    required: bool = True
    reviewed: bool = False


class Plan(Samples):
    rules: list[Rule] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def consistent(self) -> "Plan":
        targets = fields(self.target)
        sources = {path for record in self.records for path in fields(record)}
        if len({r.target for r in self.rules}) != len(self.rules):
            raise ValueError("Each target field may be mapped only once")
        if {r.target for r in self.rules} != set(targets):
            raise ValueError("Every target field must be mapped or explicitly omitted")
        for rule in self.rules:
            if not rule.reviewed:
                raise ValueError("Review every mapping before running the conversion")
            if rule.operation != "omit" and rule.source not in sources:
                raise ValueError("Choose an existing source field for each mapping")
        if all(rule.operation == "omit" for rule in self.rules):
            raise ValueError("Map at least one target field")
        return self

    def runtime_rules(self) -> list[dict[str, Any]]:
        targets = fields(self.target)
        return [
            {
                **rule.model_dump(),
                "target_type": conversion_runtime.value_type(targets[rule.target]),
            }
            for rule in self.rules
        ]


@router.post("/suggest")
def suggest(request: Samples) -> dict[str, Any]:
    source_fields = _source_fields(request.records)
    if len(source_fields) > 100:
        raise HTTPException(422, "Use at most 100 distinct source fields")
    profiles = profile_fields(request.records, (field.json_path for field in source_fields))
    candidates = map_fields(source_fields, profiles, _target_fields(request.target))
    source_by_json_path = {
        field.json_path: path
        for field, path in zip(source_fields, _source_paths(request.records), strict=True)
    }
    by_target: dict[str, list[Any]] = {}
    for candidate in candidates:
        if candidate.canonical_path is not None:
            by_target.setdefault(candidate.canonical_path, []).append(candidate)
    rules = []
    for target in fields(request.target):
        options = sorted(by_target.get(target, []), key=lambda candidate: -candidate.score)
        chosen = (
            options[0] if options and options[0].status is MappingStatus.HIGH_CONFIDENCE else None
        )
        source = source_by_json_path.get(chosen.external_path, "") if chosen else ""
        rules.append(
            {
                "source": source,
                "target": target,
                "operation": "copy",
                "required": True,
                "reviewed": False,
                "reason": "; ".join(chosen.reasons)
                if chosen and chosen.reasons
                else "Evidence-backed field match"
                if chosen
                else "No safe evidence-backed source suggestion",
                "score": chosen.score if chosen else 0,
                "status": chosen.status if chosen else MappingStatus.UNRESOLVED,
                "evidence": chosen.evidence.model_dump(mode="json")
                if chosen and chosen.evidence
                else None,
            }
        )
    return {"sources": _source_paths(request.records), "rules": rules}


def _source_paths(records: list[dict[str, Any]]) -> tuple[str, ...]:
    paths: dict[str, None] = {}
    for record in records:
        for path in fields(record):
            paths.setdefault(path, None)
    return tuple(paths)


@router.post("/preview")
def preview(request: Plan) -> dict[str, Any]:
    return conversion_runtime.transform_records(request.records, request.runtime_rules())


@router.post("/export")
def export(request: Plan) -> dict[str, str]:
    result = preview(request)
    if result["invalid"]:
        raise HTTPException(422, "Resolve all record errors before exporting")
    runtime = inspect.getsource(conversion_runtime)
    script = (
        runtime
        + "\n\nRULES = "
        + repr(request.runtime_rules())
        + """

if __name__ == "__main__":
    import json
    import sys

    records = json.load(sys.stdin)
    if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
        raise SystemExit("Input must be a JSON array of objects")
    result = transform_records(records, RULES)
    if result["invalid"]:
        json.dump(result["rows"], sys.stderr, indent=2, allow_nan=False)
        raise SystemExit(1)
    json.dump(result["output"], sys.stdout, indent=2, allow_nan=False)
    sys.stdout.write("\\n")
"""
    )
    return {"code": script}
