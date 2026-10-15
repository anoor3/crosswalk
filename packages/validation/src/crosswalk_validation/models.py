from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class FeedbackKind(StrEnum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    UNCLEAR = "UNCLEAR"
    MISSING = "MISSING"


class Feedback(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    field_path: str = Field(min_length=1)
    kind: FeedbackKind
    note: str = Field(default="", max_length=2000)


class ValidationSession(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    reviewer_id: str = Field(min_length=1)
    started_at: datetime
    feedback: tuple[Feedback, ...] = ()

    def add_feedback(self, item: Feedback) -> "ValidationSession":
        return self.model_copy(update={"feedback": (*self.feedback, item)})
