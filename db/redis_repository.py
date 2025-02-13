from db.redis_db import get_redis
import json

class RedisRepository:
    @staticmethod
    async def save_bot(bot_id: int, bot_data: dict):
        async with get_redis() as redis:
            await redis.hset(f"bot:{bot_id}", mapping=bot_data)

    @staticmethod
    async def get_bot(bot_id: int) -> dict:
        async with get_redis() as redis:
            bot_data = await redis.hgetall(f"bot:{bot_id}")
        return bot_data

    @staticmethod
    async def update_bot_field(bot_id: int, field: str, value: str):
        async with get_redis() as redis:
            await redis.hset(f"bot:{bot_id}", field, value)

    @staticmethod
    async def delete_bot(bot_id: int):
        async with get_redis() as redis:
            await redis.delete(f"bot:{bot_id}")

    @staticmethod
    async def get_all_bots() -> list:
        async with get_redis() as redis:
            keys = await redis.keys("bot:*")
            bots = []
            for key in keys:
                bot_data = await redis.hgetall(key)
                bots.append(bot_data)
        return bots