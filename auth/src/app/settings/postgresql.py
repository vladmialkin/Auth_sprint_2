from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from app.settings.base import Settings


class PostgreSQLSettings(Settings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DSN: str | None = None

    LOG_QUERIES: bool = False

    @field_validator("DSN", mode="before")
    @classmethod
    def assemble_dsn(
        cls, _: str | None, info: FieldValidationInfo
    ) -> PostgresDsn:
        scheme = "postgresql+asyncpg"
        user = info.data["POSTGRES_USER"]
        password = info.data["POSTGRES_PASSWORD"].get_secret_value()
        host = info.data["POSTGRES_HOST"]
        port = info.data["POSTGRES_PORT"]
        db = info.data["POSTGRES_DB"]

        url = f"{scheme}://{user}:{password}@{host}:{port}/{db}"
        return PostgresDsn(url).unicode_string()


settings = PostgreSQLSettings()
