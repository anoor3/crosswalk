from pydantic import BaseModel, ConfigDict, Field


class AuthPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = False
    header_name: str = Field(default="Authorization", min_length=1)

    def accepts(self, header: str | None) -> bool:
        return not self.enabled or bool(header and header.strip())
