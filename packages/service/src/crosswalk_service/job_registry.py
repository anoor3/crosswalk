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

    def update_for_tenant(self, tenant_id: str, job: Job) -> Job:
        current = self.get_for_tenant(tenant_id, job.id)
        if current is None:
            raise KeyError(job.id)
        return self.update(job)

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def has(self, job_id: str) -> bool:
        return job_id in self._jobs

    def get_for_tenant(self, tenant_id: str, job_id: str) -> Job | None:
        job = self.get(job_id)
        return job if job and job.tenant_id == tenant_id else None

    def status(self, job_id: str) -> JobStatus | None:
        job = self.get(job_id)
        return job.status if job else None

    def status_for_tenant(self, tenant_id: str, job_id: str) -> JobStatus | None:
        job = self.get_for_tenant(tenant_id, job_id)
        return job.status if job else None

    def statuses_for_tenant(self, tenant_id: str) -> tuple[JobStatus, ...]:
        return tuple(job.status for job in self.snapshot_for_tenant(tenant_id))

    def kinds_for_tenant(self, tenant_id: str) -> tuple[str, ...]:
        return tuple(job.kind for job in self.snapshot_for_tenant(tenant_id))

    def find_by_status(self, status: JobStatus) -> tuple[Job, ...]:
        return tuple(job for job in self._jobs.values() if job.status is status)

    def find_by_kind(self, kind: str) -> tuple[Job, ...]:
        return tuple(job for job in self._jobs.values() if job.kind == kind)

    def find_for_tenant(self, tenant_id: str, status: JobStatus | None = None) -> tuple[Job, ...]:
        jobs = self.snapshot_for_tenant(tenant_id)
        return tuple(job for job in jobs if status is None or job.status is status)

    def count_by_status(self, status: JobStatus) -> int:
        return len(self.find_by_status(status))

    def count_by_kind(self, kind: str) -> int:
        return len(self.find_by_kind(kind))

    def snapshot_for_tenant(self, tenant_id: str) -> tuple[Job, ...]:
        return tuple(job for job in self._jobs.values() if job.tenant_id == tenant_id)

    def count_for_tenant(self, tenant_id: str) -> int:
        return sum(job.tenant_id == tenant_id for job in self._jobs.values())

    def count(self) -> int:
        return len(self._jobs)

    def snapshot(self) -> tuple[Job, ...]:
        return tuple(self._jobs.values())

    def ids(self) -> tuple[str, ...]:
        return tuple(self._jobs)

    def ids_for_tenant(self, tenant_id: str) -> tuple[str, ...]:
        return tuple(job.id for job in self.snapshot_for_tenant(tenant_id))

    def remove(self, job_id: str) -> Job | None:
        return self._jobs.pop(job_id, None)

    def remove_for_tenant(self, tenant_id: str, job_id: str) -> Job | None:
        job = self.get_for_tenant(tenant_id, job_id)
        return self.remove(job_id) if job else None

    def clear(self) -> None:
        self._jobs.clear()

    def clear_for_tenant(self, tenant_id: str) -> int:
        ids = self.ids_for_tenant(tenant_id)
        for job_id in ids:
            self._jobs.pop(job_id, None)
        return len(ids)
