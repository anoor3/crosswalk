import pytest
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import JobRegistry


def test_update_for_tenant_rejects_cross_tenant_job() -> None:
    registry = JobRegistry()
    registry.add(Job(id="j1", tenant_id="t1", kind="sync"))  # type: ignore[call-arg]

    with pytest.raises(KeyError):
        registry.update_for_tenant(
            "t2",
            Job(id="j1", tenant_id="t1", kind="sync", status=JobStatus.RUNNING),  # type: ignore[call-arg]
        )
