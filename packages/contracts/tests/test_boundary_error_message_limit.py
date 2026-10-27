import pytest
from crosswalk_contracts import ErrorEnvelope
from pydantic import ValidationError


def test_error_envelope_rejects_long_message() -> None:
    with pytest.raises(ValidationError):
        ErrorEnvelope(code="x", message="x" * 1001, trace_id="t")
