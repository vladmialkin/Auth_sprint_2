from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from ..db.elastic import get_elastic
from ..db.redis import get_redis

RedisConnection = Annotated[Redis, Depends(get_redis)]
ESConnection = Annotated[Redis, Depends(get_elastic)]
