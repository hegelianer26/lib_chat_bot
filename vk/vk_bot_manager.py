from redis_repository import RedisRepository
from vkbottle.bot import Bot
from vk_handler import VKHandler
import asyncio
from vkbottle.http import AiohttpClient
from vkbottle.api import API

class VKBotManager:
    def __init__(self):
        self.redis_repo = RedisRepository()
        self.bots = {}  # Словарь для хранения запущенных ботов

    async def start(self):
        """Запускает загрузку ботов из Redis и подписку на обновления."""
        await self.clear_invalid_bots()
        await self.load_bots_from_redis()
        await self.subscribe_to_redis()

    async def clear_invalid_bots(self):
        """Удаляет из Redis ботов, у которых нет валидных данных."""
        async with RedisRepository.get_connection() as redis:
            running_bot_ids = await redis.smembers("running_bots")
            for bot_id in running_bot_ids:
                bot_data = await RedisRepository.get_bot(bot_id)
                if not bot_data or not bot_data.get('vk_token'):
                    print(f"Удаляю невалидного бота {bot_id} из running_bots")
                    await redis.srem("running_bots", bot_id)

    async def load_bots_from_redis(self):
        """Загружает список работающих ботов и запускает их."""
        async with RedisRepository.get_connection() as redis:
            bot_ids = await redis.smembers("running_bots")  
            for bot_id in bot_ids:
                bot_data = await RedisRepository.get_bot(bot_id)
                if bot_data and bot_data.get('vk_token'):
                    await self.start_bot(bot_data)

    async def subscribe_to_redis(self):
        async with RedisRepository.subscribe('bot_updates') as pubsub:
            print("Subscribed to 'bot_updates' channel")
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    bot_id = int(message['data'])
                    bot_data = await RedisRepository.get_bot(bot_id)

                    if not bot_data:
                        print(f"Бот {bot_id} не найден в Redis")
                        continue

                    vk_is_active = bot_data.get('vk_is_active', "false") == "true"

                    if vk_is_active:
                        await self.start_bot(bot_data)  # Запускаем, если активен
                    else:
                        await self.stop_bot(bot_id)  # Останавливаем, если выключен

    async def start_bot(self, bot_data):
        bot_id = int(bot_data['id'])
        bot_token = bot_data.get('vk_token')
        vk_is_active = bot_data.get('vk_is_active', "false") == "true"  # Преобразуем строку в bool

        if not vk_is_active:
            print(f"Бот {bot_id} неактивен, запуск отменен.")
            return

        if not bot_token:
            print(f"Ошибка: Отсутствует токен для бота {bot_id}")
            return

        # Проверка на дублирование токенов
        async with RedisRepository.get_connection() as redis:
            existing_bots = await redis.smembers("running_bots")

            for existing_bot_id in existing_bots:
                try:
                    existing_bot_id = int(existing_bot_id)
                except ValueError:
                    continue

                existing_bot_data = await RedisRepository.get_bot(existing_bot_id)
                if existing_bot_data and existing_bot_data.get("vk_token") == bot_token:
                    if existing_bot_id != bot_id:
                        print(f"Ошибка: Бот {bot_id} использует дублирующийся токен (совпадает с ботом {existing_bot_id})")
                        return

        # Запускаем бота
        api_url = "http://0.0.0.0:8000/api"
        upload_dir = "uploads"

        http_client = AiohttpClient()
        bot = Bot(token=bot_token, api=API(token=bot_token, http_client=http_client))

        vk_handler = VKHandler(bot, bot_id, api_url, upload_dir)
        vk_handler.start()

        self.bots[bot_id] = {
            "handler": vk_handler,
            "http_client": http_client
        }

        async with RedisRepository.get_connection() as redis:
            await redis.sadd("running_bots", bot_id)

        print(f"Бот {bot_id} запущен")

    async def stop_bot(self, bot_id):
        """Останавливает бота и удаляет его из Redis."""
        if await RedisRepository.is_bot_running(bot_id):
            if bot_id in self.bots:
                self.bots[bot_id]["handler"].stop()
                del self.bots[bot_id]

            await RedisRepository.mark_bot_as_stopped(bot_id)

            # Удаляем бота из running_bots в Redis
            async with RedisRepository.get_connection() as redis:
                await redis.srem("running_bots", bot_id)

            print(f"Бот {bot_id} остановлен")

    async def restart_bot(self, bot_id):
        """Перезапускает бота."""
        await self.stop_bot(bot_id)
        bot_data = await RedisRepository.get_bot(bot_id)
        if bot_data and bot_data.get('vk_token'):
            await self.start_bot(bot_data)