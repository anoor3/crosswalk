import pytest
from crosswalk_contracts import ErrorEnvelope, HealthResponse, Page


def test_page_preserves_item_order_and_cursor() -> None:
    page = Page[int](items=(1, 2), next_cursor="next")
    assert page.items == (1, 2)
    assert page.next_cursor == "next"


def test_health_status_is_restricted() -> None:
    with pytest.raises(ValueError):
        HealthResponse(status="unknown", version="1")
    assert ErrorEnvelope(code="bad_request", message="bad", trace_id="t").code == "bad_request"
