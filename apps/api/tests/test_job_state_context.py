from fastapi.testclient import TestClient

from crosswalk_api import create_app
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import ServiceContext


def test_job_state_reads_registry_status() -> None:
    context = ServiceContext()
    context.jobs.add(Job(id="j1", tenant_id="tenant-a", kind="sync", status=JobStatus.FAILED))

    response = TestClient(create_app(context=context)).get("/jobs/j1/state")

    assert response.json() == {"id": "j1", "status": "FAILED"}
