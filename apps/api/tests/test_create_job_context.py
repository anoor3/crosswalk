from fastapi.testclient import TestClient

from crosswalk_api import create_app
from crosswalk_service import ServiceContext


def test_create_job_registers_and_queues_job() -> None:
    context = ServiceContext()
    response = TestClient(create_app(context=context)).post(
        "/jobs", json={"tenant_id": "tenant-a", "kind": "discover"}
    )

    job_id = response.json()["id"]
    assert context.jobs.get(job_id) is not None
    assert context.queue.contains(job_id)
