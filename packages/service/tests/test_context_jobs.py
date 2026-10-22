from crosswalk_service import ServiceContext


def test_context_provides_job_registry() -> None:
    assert ServiceContext().jobs.count() == 0
