from crosswalk_jobs import Job, JobStatus


class JobRegistry:
    """Tenant-neutral in-memory job view for the local service boundary."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def add(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job

    def update(self, job: Job) -> Job:
        if job.id not in self._jobs:
            raise KeyError(job.id)
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def get_for_tenant(self, tenant_id: str, job_id: str) -> Job | None:
        job = self.get(job_id)
        return job if job and job.tenant_id == tenant_id else None

    def status(self, job_id: str) -> JobStatus | None:
        job = self.get(job_id)
        return job.status if job else None

    def status_for_tenant(self, tenant_id: str, job_id: str) -> JobStatus | None:
        job = self.get_for_tenant(tenant_id, job_id)
        return job.status if job else None

    def snapshot_for_tenant(self, tenant_id: str) -> tuple[Job, ...]:
        return tuple(job for job in self._jobs.values() if job.tenant_id == tenant_id)

    def count(self) -> int:
        return len(self._jobs)

    def snapshot(self) -> tuple[Job, ...]:
        return tuple(self._jobs.values())

    def remove(self, job_id: str) -> Job | None:
        return self._jobs.pop(job_id, None)

    def clear(self) -> None:
        self._jobs.clear()
