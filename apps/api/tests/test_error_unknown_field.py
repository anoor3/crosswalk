import pytest
from crosswalk_contracts import ErrorEnvelope
from pydantic import ValidationError


def test_error_envelope_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        ErrorEnvelope(code="bad", message="invalid", trace_id="t1", detail="x")
