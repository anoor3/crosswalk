from __future__ import annotations

from random import Random

from pydantic import BaseModel, ConfigDict, Field


class RetryPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_attempts: int = Field(default=3, ge=1, le=10)
    base_delay_seconds: float = Field(default=0.25, ge=0, le=60)
    max_delay_seconds: float = Field(default=30, ge=0, le=300)
    jitter_ratio: float = Field(default=0.1, ge=0, le=1)


def retry_delay(policy: RetryPolicy, attempt: int, seed: int = 0) -> float:
    if attempt < 1 or attempt > policy.max_attempts:
        raise ValueError("attempt must be within policy bounds")
    base = min(policy.max_delay_seconds, policy.base_delay_seconds * (2 ** (attempt - 1)))
    jitter = float(
        Random(seed + attempt).uniform(  # noqa: S311 - deterministic jitter only
            -policy.jitter_ratio, policy.jitter_ratio
        )
    )
    return float(max(0.0, min(policy.max_delay_seconds, base * (1 + jitter))))
