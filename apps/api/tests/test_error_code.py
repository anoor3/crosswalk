import pytest
from crosswalk_contracts import ErrorEnvelope
from pydantic import ValidationError


def test_error_envelope_requires_code() -> None:
    with pytest.raises(ValidationError):
        ErrorEnvelope(code="", message="invalid", trace_id="t1")
