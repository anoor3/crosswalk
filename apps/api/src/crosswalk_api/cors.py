from pydantic import BaseModel, ConfigDict


class CorsPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    allowed_origins: tuple[str, ...] = ()

    def allows(self, origin: str) -> bool:
        return origin in self.allowed_origins
