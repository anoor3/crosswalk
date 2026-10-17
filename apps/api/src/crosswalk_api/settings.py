from pydantic import BaseModel, ConfigDict, Field


class ApiSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    environment: str = Field(default="local", pattern=r"^(local|staging|production)$")
    version: str = Field(default="development", min_length=1)
    enable_docs: bool = True
