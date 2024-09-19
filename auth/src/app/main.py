from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api import v1_router
from app.db import postgresql, redis
from app.settings.api import settings as api_settings
from app.settings.postgresql import settings as postgresql_settings
from app.settings.redis import settings as redis_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis.redis_conn = Redis.from_url(redis_settings.DSN)
    postgresql.async_engine = create_async_engine(
        postgresql_settings.DSN,
        echo=postgresql_settings.LOG_QUERIES,
    )
    postgresql.async_session = async_sessionmaker(
        postgresql.async_engine, expire_on_commit=False
    )
    yield
    await redis.redis_conn.close()
    await postgresql.async_engine.dispose()


app = FastAPI(
    title=api_settings.TITLE,
    openapi_url=api_settings.OPENAPI_URL,
    docs_url=api_settings.DOCS_URL,
    redoc_url=api_settings.REDOC_URL,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(v1_router)
