from pydantic import BaseModel, ConfigDict, Field


class ServiceConfig(BaseModel):
    """Small immutable runtime configuration for local service composition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(default="crosswalk-api", min_length=1)
    version: str = Field(default="development", min_length=1)
    environment: str = Field(default="local", min_length=1)
