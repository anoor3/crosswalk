from crosswalk_service import ServiceContext


def test_contexts_have_independent_job_registries() -> None:
    first = ServiceContext()
    second = ServiceContext()

    assert first.jobs is not second.jobs
