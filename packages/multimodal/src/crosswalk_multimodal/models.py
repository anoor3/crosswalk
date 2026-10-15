from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class InputKind(StrEnum):
    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class MediaInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: InputKind
    uri: str = Field(min_length=1)
    media_type: str = Field(min_length=1)
    byte_size: int = Field(ge=0)


class TextSpan(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(min_length=1, max_length=10_000)
    page: int | None = Field(default=None, ge=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
