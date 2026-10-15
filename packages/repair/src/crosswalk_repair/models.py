from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from crosswalk_drift import DriftEvent


class RepairStatus(StrEnum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RepairProposal(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    drift: DriftEvent
    replacement_path: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    evidence: tuple[str, ...] = ()
    status: RepairStatus = RepairStatus.PROPOSED

    def approve(self) -> "RepairProposal":
        return self.model_copy(update={"status": RepairStatus.APPROVED})
