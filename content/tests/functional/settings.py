from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve(strict=True).parent


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR.joinpath('.env'), extra='allow', case_sensitive=True)
    es_host: str
    es_port: int
    movies_index_name: str
    persons_index_name: str

    redis_host: str
    redis_port: str

    service_url: str


test_settings = TestSettings()
