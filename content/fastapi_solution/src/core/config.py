from logging import config as logging_config
from pathlib import Path

from .logger import LOGGING
from pydantic_settings import BaseSettings, SettingsConfigDict

logging_config.dictConfig(LOGGING)


ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR.joinpath(".env"), case_sensitive=True, extra="allow")

    # REDIS
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    
    # ELASTIC
    ELASTIC_HOST: str
    ELASTIC_PORT: int = 9200

    # PROJECT
    PROJECT_NAME: str = "Default project name"

    # RETRY POLICY
    MAX_TRIES: int = 10

    AUTH_API_URL=""
    JWT_ALGORITHM: str = "HS256"
    AUDIENCE: str = "fastapi"
    SECRET: str = "SECRET"

settings = Settings()