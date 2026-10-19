from dataclasses import dataclass


@dataclass(frozen=True)
class Readiness:
    """Explicit local readiness state for future dependency checks."""

    ready: bool = True

    @property
    def status(self) -> str:
        return "ok" if self.ready else "degraded"
