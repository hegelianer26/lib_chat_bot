from redis_repository import RedisRepository
from vkbottle.bot import Bot
from vk_handler import VKHandler
import asyncio
from vkbottle.http import AiohttpClient
from vkbottle.api import API
import threading

class VKBotManager:
    def __init__(self):
        self.redis_repo = RedisRepository()
        self.bots = {}  # Dictionary to store bot tasks

    async def start(self):
        await self.load_bots_from_redis()
        await self.subscribe_to_redis()

    async def load_bots_from_redis(self):
        async with RedisRepository.get_connection() as redis:
            keys = await redis.keys('bot:*')  # Get all bot keys
            for key in keys:
                bot_id = int(key.split(":")[1])
                bot_data = await RedisRepository.get_bot(bot_id)
                if bot_data and bot_data.get('has_vk') and bot_data.get('vk_is_active') == 'True':
                    await self.start_bot(bot_data)

    async def subscribe_to_redis(self):
        async with RedisRepository.subscribe('bot_updates') as pubsub:
            print("Subscribed to 'bot_updates' channel")
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    print(f"Received message: {message}")
                    bot_id = int(message['data'])
                    bot_data = await RedisRepository.get_bot(bot_id)
                    print(f"Bot data for ID {bot_id}: {bot_data}")  # Debug log
                    await self.start_bot(bot_data)



    async def start_bot(self, bot_data):
        bot_id = int(bot_data['id'])
        bot_token = bot_data.get('vk_token')
        if not bot_token:
            print(f"Ошибка: Отсутствует токен для бота {bot_id}")
            return

        if bot_id in self.bots:
            print(f"Бот {bot_id} уже запущен")
            return

        api_url = "http://0.0.0.0:8000/api"
        upload_dir = "uploads"

        # Создаем отдельный HTTP-клиент для бота
        http_client = AiohttpClient()
        bot = Bot(token=bot_token, api=API(token=bot_token, http_client=http_client))

        vk_handler = VKHandler(bot, bot_id, api_url, upload_dir)

        # Запускаем бота
        vk_handler.start()

        self.bots[bot_id] = {
            "handler": vk_handler,
            "http_client": http_client
        }

        await RedisRepository.mark_bot_as_running(bot_id)
        print(f"Бот {bot_id} запущен")
        
    async def stop_bot(self, bot_id):
        if await RedisRepository.is_bot_running(bot_id):
            if bot_id in self.bots:
                self.bots[bot_id].stop()  # Останавливаем бота
                del self.bots[bot_id]
            await RedisRepository.mark_bot_as_stopped(bot_id)
            print(f"Bot {bot_id} stopped")