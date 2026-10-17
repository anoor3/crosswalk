from crosswalk_service import ServiceContext


def test_context_provides_queue() -> None:
    assert ServiceContext().queue is not None
