"""Sample-to-target mapping and explicit, bounded conversion plans."""

import inspect
import json
import re
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    source_fields: dict[str, Any] = {}
    for record in request.records:
        source_fields.update(fields(record))
    if len(source_fields) > 100:
        raise HTTPException(422, "Use at most 100 distinct source fields")

    def normalized(path: str) -> str:
        return re.sub(r"[^a-z0-9]", "", path.rsplit("/", 1)[-1].lower())

    rules = []
    for target in fields(request.target):
        matches = [
            path
            for path in source_fields
            if normalized(target) and normalized(path) == normalized(target)
        ]
        source = target if target in source_fields else matches[0] if len(matches) == 1 else ""
        rules.append(
            {
                "source": source,
                "target": target,
                "operation": "copy",
                "required": True,
                "reviewed": False,
                "reason": "Same field name" if source else "Choose a source",
            }
        )
    return {"sources": list(source_fields), "rules": rules}


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
