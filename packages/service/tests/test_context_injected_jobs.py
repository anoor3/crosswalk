from crosswalk_service import JobRegistry, ServiceContext


def test_context_accepts_injected_job_registry() -> None:
    jobs = JobRegistry()

    assert ServiceContext(jobs=jobs).jobs is jobs
