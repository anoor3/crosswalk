from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RollbackStatus(StrEnum):
    READY = "READY"
    EXECUTED = "EXECUTED"


class RollbackPlan(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    release_id: str = Field(min_length=1)
    previous_release_id: str = Field(min_length=1)
    status: RollbackStatus = RollbackStatus.READY

    def execute(self) -> "RollbackPlan":
        return self.model_copy(update={"status": RollbackStatus.EXECUTED})
