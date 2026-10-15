from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class DeploymentConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: Environment
    service_name: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9-]{1,62}$")
    image: str = Field(min_length=1)
    health_path: str = Field(default="/health", pattern=r"^/[a-zA-Z0-9/_-]*$")
    https_required: bool = True
    migrations_required: bool = True
