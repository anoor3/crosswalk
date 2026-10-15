from pydantic import BaseModel, ConfigDict, Field

_CONFIG = ConfigDict(frozen=True, extra="forbid")


class AdapterField(BaseModel):
    model_config = _CONFIG

    source_path: str = Field(min_length=1)
    canonical_path: str = Field(min_length=1)
    required: bool = False


class AdapterSpec(BaseModel):
    model_config = _CONFIG

    name: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]{1,63}$")
    source_name: str = Field(min_length=1)
    fields: tuple[AdapterField, ...] = Field(min_length=1)
