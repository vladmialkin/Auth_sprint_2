import pickle
from logging import getLogger
from typing import Any, Coroutine

import backoff
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError

from ..core.config import settings
from ..repository.base import InMemoryRepository

logger = getLogger(__name__)


class RedisRepository(InMemoryRepository):
    def __init__(self, redis_conn: Redis, ttl: int | None = None) -> None:
        self._conn = redis_conn
        self._ttl = ttl

    @backoff.on_exception(
        backoff.expo,
        (ConnectionError, TimeoutError),
        max_tries=settings.MAX_TRIES,
        logger=logger,
    )
    async def get(self, slug: str, **kwargs) -> Coroutine[Any, Any, Any | None]:
        key = self._compute_key(slug=slug, **kwargs)
        value = await self._conn.get(key)

        if not value:
            return None

        return pickle.loads(value)

    @backoff.on_exception(
        backoff.expo,
        (ConnectionError, TimeoutError),
        max_tries=settings.MAX_TRIES,
        logger=logger,
    )
    async def add(self, slug: str, value: Any, **kwargs) -> Coroutine[Any, Any, None]:
        key = self._compute_key(slug=slug, **kwargs)
        await self._conn.set(key, pickle.dumps(value), ex=self._ttl)
