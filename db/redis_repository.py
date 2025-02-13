from db.redis_db import get_redis
import json

class RedisRepository:
    @staticmethod
    async def save_bot(bot_id: int, bot_data: dict):
        # Convert bool values to strings for Redis compatibility
        processed_data = {k: str(v).lower() if isinstance(v, bool) else v for k, v in bot_data.items()}
        async with get_redis() as redis:
            await redis.hset(f"bot:{bot_id}", mapping=processed_data)

    @staticmethod
    async def get_bot(bot_id: int) -> dict:
        async with get_redis() as redis:
            bot_data = await redis.hgetall(f"bot:{bot_id}")
        
        # Convert string representations of bools back to bool objects
        if bot_data:
            for key, value in bot_data.items():
                if value.lower() == "true":
                    bot_data[key] = True
                elif value.lower() == "false":
                    bot_data[key] = False
        return bot_data

    @staticmethod
    async def update_bot_field(bot_id: int, field: str, value: str):
        async with get_redis() as redis:
            await redis.hset(f"bot:{bot_id}", field, str(value).lower() if isinstance(value, bool) else value)

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
                # Convert string representations of bools back to bool objects
                if bot_data:
                    for k, v in bot_data.items():
                        if v.lower() == "true":
                            bot_data[k] = True
                        elif v.lower() == "false":
                            bot_data[k] = False
                bots.append(bot_data)
        return bots