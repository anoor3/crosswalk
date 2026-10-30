from crosswalk_api import create_app
from crosswalk_jobs import Job, JobStatus
from crosswalk_service import ServiceContext
from fastapi.testclient import TestClient


def test_job_status_reads_registry_state() -> None:
    context = ServiceContext()
    context.jobs.add(Job(id="j1", tenant_id="tenant-a", kind="sync", status=JobStatus.RUNNING))

    response = TestClient(create_app(context=context)).get("/jobs/j1")

    assert response.json() == {"id": "j1", "status": "running", "progress": 0}
