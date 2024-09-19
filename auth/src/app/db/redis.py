from redis.asyncio import Redis

redis_conn: Redis | None = None


async def get_redis() -> Redis | None:
    return redis_conn
