from __future__ import annotations

import os

from pydantic import BaseModel, ConfigDict, Field


class ApiSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: str = Field(default="local", pattern=r"^(local|staging|production)$")
    version: str = Field(default="development", min_length=1)
    enable_docs: bool = True
    review_database: str | None = None

    @classmethod
    def from_environment(cls) -> ApiSettings:
        return cls(
            environment=os.getenv("CROSSWALK_ENVIRONMENT", "local"),
            version=os.getenv("CROSSWALK_VERSION", "development"),
            review_database=os.getenv("CROSSWALK_REVIEW_DATABASE"),
        )
