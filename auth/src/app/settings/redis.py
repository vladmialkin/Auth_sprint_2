from pydantic import RedisDsn, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from app.settings.base import Settings


class RedisSettings(Settings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    DSN: str | None = None

    @field_validator("DSN", mode="before")
    @classmethod
    def assemble_dsn(cls, _: str | None, info: FieldValidationInfo) -> str:
        scheme = "redis"
        host = info.data["REDIS_HOST"]
        port = info.data["REDIS_PORT"]
        db = info.data["REDIS_DB"]

        url = f"{scheme}://{host}:{port}/{db}"
        return RedisDsn(url).unicode_string()


settings = RedisSettings()
