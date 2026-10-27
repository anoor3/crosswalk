import pytest
from crosswalk_contracts import Page
from pydantic import ValidationError


def test_page_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Page[int](items=(), extra="x")  # type: ignore[call-arg]
