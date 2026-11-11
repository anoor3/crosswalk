"""Portable conversion runtime shared by the preview and exported adapters."""

import math
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any


def validate_json(value: Any, depth: int = 0) -> None:
    """Keep browser, API, and downloaded adapter numeric behavior consistent."""
    if depth > 16:
        raise ValueError("JSON may be nested at most 16 levels deep")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value) or abs(value) > 9_007_199_254_740_991:
            raise ValueError("Number is outside the supported range; encode large IDs as strings")
    elif isinstance(value, dict):
        for child in value.values():
            validate_json(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            validate_json(child, depth + 1)


def read_pointer(record: dict[str, Any], pointer: str) -> Any:
    value: Any = record
    for token in pointer.split("/")[1:]:
        key = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or key not in value:
            raise ValueError("Source field is missing")
        value = value[key]
    return value


def write_pointer(record: dict[str, Any], pointer: str, value: Any) -> None:
    tokens = [part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:]]
    for token in tokens[:-1]:
        record = record.setdefault(token, {})
    record[tokens[-1]] = value


def value_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


def convert_value(value: Any, operation: str) -> Any:
    if operation == "copy":
        return value
    if value is None or isinstance(value, (bool, list, dict)):
        raise ValueError("Conversion requires a non-null string or number")
    if operation == "text":
        return str(value)
    if operation in ("number", "integer", "cents_to_dollars"):
        try:
            number = Decimal(str(value))
        except InvalidOperation as error:
            raise ValueError("Value is not a number") from error
        if not number.is_finite():
            raise ValueError("Number must be finite")
        if number.copy_abs() > 9_007_199_254_740_991:
            raise ValueError("Number is outside the supported range")
        if operation in ("integer", "cents_to_dollars") and number != number.to_integral_value():
            raise ValueError("Expected a whole number; rounding is not applied")
        if operation == "integer":
            return int(number)
        result = float(number / 100 if operation == "cents_to_dollars" else number)
        if not math.isfinite(result):
            raise ValueError("Number is out of range")
        if number != 0 and result == 0:
            raise ValueError("Number is too small to represent without losing its value")
        return result
    formats = {"date_iso": "%Y-%m-%d", "date_us": "%m/%d/%Y", "date_day_first": "%d/%m/%Y"}
    if operation in formats:
        try:
            return datetime.strptime(str(value), formats[operation]).date().isoformat()
        except ValueError as error:
            raise ValueError(f"Expected a valid date in {formats[operation]} format") from error
    raise ValueError("Unknown conversion")


def transform_records(records: list[dict[str, Any]], rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Invalid records are excluded from output; errors retain their source index."""
    output: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        converted: dict[str, Any] = {}
        errors: list[dict[str, str]] = []
        try:
            validate_json(record)
        except (ValueError, OverflowError) as error:
            rows.append(
                {"index": index, "output": {}, "errors": [{"target": "", "message": str(error)}]}
            )
            continue
        for rule in rules:
            if rule["operation"] == "omit":
                continue
            try:
                try:
                    value = read_pointer(record, rule["source"])
                except ValueError:
                    if not rule["required"]:
                        continue
                    raise
                if value is None and not rule["required"]:
                    write_pointer(converted, rule["target"], None)
                    continue
                value = convert_value(value, rule["operation"])
                if value is None and rule["required"]:
                    raise ValueError("Required field is null")
                if value is not None and value_type(value) != rule["target_type"]:
                    raise ValueError(f"Expected {rule['target_type']}, got {value_type(value)}")
                write_pointer(converted, rule["target"], value)
            except (ValueError, OverflowError) as error:
                errors.append({"target": rule["target"], "message": str(error)})
        rows.append({"index": index, "output": converted, "errors": errors})
        if not errors:
            output.append(converted)
    return {
        "output": output,
        "rows": rows,
        "valid": len(output),
        "invalid": len(records) - len(output),
    }
