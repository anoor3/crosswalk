from datetime import UTC, datetime

import pytest
from crosswalk_jobs import Job
from crosswalk_service import JobRegistry


def test_job_registry_rejects_update_for_missing_job() -> None:
    job = Job(id="missing", tenant_id="t1", kind="discover", created_at=datetime.now(UTC))

    with pytest.raises(KeyError):
        JobRegistry().update(job)
