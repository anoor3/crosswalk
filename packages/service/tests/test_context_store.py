from crosswalk_service import ServiceContext


def test_context_provides_store() -> None:
    assert ServiceContext().store is not None
