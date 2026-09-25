"""Unit tests for the ApiCatalog data model (Phase 2 Task 1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from crosswalk_discovery import (
    ApiCatalog,
    Endpoint,
    ExternalField,
    FieldType,
)


def _field(path: str, name: str, dt: FieldType = FieldType.STRING) -> ExternalField:
    return ExternalField(json_path=path, name=name, data_type=dt)


class TestExternalField:
    def test_minimal(self) -> None:
        f = _field("$.claimNumber", "claimNumber")
        assert f.data_type is FieldType.STRING
        assert f.required is False
        assert f.nullable is False
        assert f.enum_values == ()

    def test_enum_values_are_tuple(self) -> None:
        f = ExternalField(
            json_path="$.status",
            name="status",
            data_type=FieldType.STRING,
            enum_values=("OPEN", "CLOSED"),
        )
        assert f.enum_values == ("OPEN", "CLOSED")

    def test_frozen(self) -> None:
        f = _field("$.a", "a")
        with pytest.raises(ValidationError):
            f.name = "b"  # type: ignore[misc]


class TestEndpoint:
    def test_defaults(self) -> None:
        e = Endpoint(method="GET", path="/claims")
        assert e.tags == ()
        assert e.response_fields == ()
        assert e.response_is_collection is False


class TestApiCatalog:
    def test_endpoint_lookup(self) -> None:
        e1 = Endpoint(method="GET", path="/claims")
        e2 = Endpoint(method="GET", path="/claims/{id}")
        cat = ApiCatalog(
            title="X",
            version="1.0.0",
            openapi_version="3.1.0",
            endpoints=(e1, e2),
        )
        assert cat.endpoint("get", "/claims") is e1
        assert cat.endpoint("GET", "/claims/{id}") is e2
        assert cat.endpoint("POST", "/claims") is None

    def test_unknown_field_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ApiCatalog(
                title="X",
                version="1",
                openapi_version="3.1.0",
                bogus="nope",  # type: ignore[call-arg]
            )
