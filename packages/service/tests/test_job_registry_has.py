from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_has_reports_registered_job() -> None:
    registry = JobRegistry()
    registry.add(Job(id="j1", tenant_id="t1", kind="sync"))  # type: ignore[call-arg]

    assert registry.has("j1") is True
    assert registry.has("missing") is False
