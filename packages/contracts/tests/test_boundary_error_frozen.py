import pytest
from crosswalk_contracts import ErrorEnvelope
from pydantic import ValidationError


def test_error_envelope_is_frozen() -> None:
    value = ErrorEnvelope(code="x", message="m", trace_id="t")
    with pytest.raises(ValidationError):
        value.code = "y"  # type: ignore[misc]
