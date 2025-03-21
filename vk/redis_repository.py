from redis import asyncio as aioredis
from contextlib import asynccontextmanager
from vk_conf import Config

class RedisRepository:
    _pool = None

    @classmethod
    async def init_pool(cls):
        """Инициализация пула соединений"""
        if cls._pool is None:
            cls._pool = await aioredis.from_url(
                f"redis://:{Config.REDIS_PASSWORD}@{Config.REDIS_HOST}:{Config.REDIS_PORT}/0",
                encoding="utf-8",
                decode_responses=True,
                max_connections=10
            )
            print("Redis connection pool initialized")

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """Получение соединения из пула"""
        if cls._pool is None:
            await cls.init_pool()
        async with cls._pool.client() as redis:
            yield redis

    @staticmethod
    async def save_bot(bot_id, data):
        async with RedisRepository.get_connection() as redis:
            await redis.hset(f'bot:{bot_id}', mapping=data)

    @staticmethod
    async def delete_bot(bot_id):
        async with RedisRepository.get_connection() as redis:
            await redis.delete(f'bot:{bot_id}')
            await redis.srem('running_bots', bot_id)

    @staticmethod
    async def get_bot(bot_id):
        async with RedisRepository.get_connection() as redis:
            return await redis.hgetall(f'bot:{bot_id}')

    @staticmethod
    async def is_bot_running(bot_id):
        async with RedisRepository.get_connection() as redis:
            return bool(await redis.sismember('running_bots', bot_id))

    @staticmethod
    async def mark_bot_as_running(bot_id):
        async with RedisRepository.get_connection() as redis:
            await redis.sadd('running_bots', bot_id)

    @staticmethod
    async def mark_bot_as_stopped(bot_id):
        async with RedisRepository.get_connection() as redis:
            await redis.srem('running_bots', bot_id)


    @staticmethod
    @asynccontextmanager
    async def subscribe(channel: str):
        """Subscribe to a Redis channel"""
        async with RedisRepository.get_connection() as redis:
            pubsub = redis.pubsub()
            await pubsub.subscribe(channel)
            try:
                yield pubsub
            finally:
                await pubsub.unsubscribe(channel)


    @staticmethod
    async def add_bot_task(bot_id, task_id):
        """Добавить задачу для бота"""
        async with RedisRepository.get_connection() as redis:
            await redis.hset(f'bot_task:{bot_id}', mapping={"task_id": task_id})

    @staticmethod
    async def get_bot_task(bot_id):
        """Получить задачу для бота"""
        async with RedisRepository.get_connection() as redis:
            return await redis.hgetall(f'bot_task:{bot_id}')

    @staticmethod
    async def remove_bot_task(bot_id):
        """Удалить задачу для бота"""
        async with RedisRepository.get_connection() as redis:
            await redis.delete(f'bot_task:{bot_id}')