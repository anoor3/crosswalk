import pytest
from crosswalk_contracts import Page
from pydantic import ValidationError


def test_page_is_frozen() -> None:
    page = Page[int](items=(1,))
    with pytest.raises(ValidationError):
        page.next_cursor = "x"
