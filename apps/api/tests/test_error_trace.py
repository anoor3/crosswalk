import pytest
from crosswalk_contracts import ErrorEnvelope
from pydantic import ValidationError


def test_error_envelope_requires_trace_id() -> None:
    with pytest.raises(ValidationError):
        ErrorEnvelope(code="bad", message="invalid", trace_id="")
