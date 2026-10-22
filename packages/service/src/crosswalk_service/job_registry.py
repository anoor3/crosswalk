from crosswalk_jobs import Job, JobStatus


class JobRegistry:
    """Tenant-neutral in-memory job view for the local service boundary."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def add(self, job: Job) -> Job:
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def status(self, job_id: str) -> JobStatus | None:
        job = self.get(job_id)
        return job.status if job else None
