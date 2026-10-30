from datetime import UTC, datetime

from crosswalk_api import create_app
from crosswalk_service import ServiceContext, submit_job
from fastapi.testclient import TestClient


def test_job_list_returns_only_requested_tenant() -> None:
    context = ServiceContext()
    first = submit_job(context, "tenant-a", "discover", datetime.now(UTC))
    submit_job(context, "tenant-b", "discover", datetime.now(UTC))

    response = TestClient(create_app(context=context)).get(
        "/jobs", params={"tenant_id": "tenant-a"}
    )

    assert response.json()["items"][0]["id"] == first.id
