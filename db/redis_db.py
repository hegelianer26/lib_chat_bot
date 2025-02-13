from redis import asyncio as aioredis
from contextlib import asynccontextmanager
from config import Config

async def init_redis_pool():
    return await aioredis.from_url(
        f"redis://:{Config.REDIS_PASSWORD}@{Config.REDIS_HOST}:{Config.REDIS_PORT}/0",
        encoding="utf-8",
        decode_responses=True,
        max_connections=10  # Установите нужное количество соединений
    )

@asynccontextmanager
async def get_redis():
    if not hasattr(get_redis, 'pool'):
        get_redis.pool = await init_redis_pool()
    async with get_redis.pool.client() as redis:
        yield redis