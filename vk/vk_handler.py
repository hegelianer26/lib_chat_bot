# vk_handler.py

import logging
import asyncio
from vkbottle.bot import Bot
from api_client import APIClient
from message_handlers import MessageHandlers
from keyboard_builder import KeyboardBuilder
from vkbottle.api import API
from vkbottle.bot import BotLabeler, Message
from vkbottle.dispatch.rules.base import CommandRule
import threading
from vkbottle.tools import LoopWrapper

class VKHandler:
    def __init__(self, bot: Bot, bot_id: int, api_url: str, upload_dir: str):
        self.logger = logging.getLogger(f"VKHandler_{bot_id}")
        self.bot = bot
        self.bot_id = bot_id
        self.api_client = APIClient(api_url, self.logger)
        self.message_handlers = MessageHandlers(self)
        self.keyboard_builder = KeyboardBuilder(self)
        self.upload_dir = upload_dir
        self.polling_task = None
        self.is_active = True
        self.loop_wrapper = LoopWrapper()

        self.labeler = BotLabeler()

        @self.labeler.message(CommandRule("start"))
        async def start_handler(message: Message):
            await message.answer("Hello! This is your bot.")

        self.bot.labeler = self.labeler
        self.thread = None

        self.setup_logging()
        self.setup_handlers()

    def setup_logging(self):
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.info(f"VKHandler initialized for bot ID: {self.bot_id}")

    def setup_handlers(self):
        self.message_handlers.setup()

    async def get_or_create_user(self, message):
        try:
            # Получаем информацию о пользователе через VK API
            user_info = await self.bot.api.users.get(user_ids=[message.from_id], fields=["first_name", "last_name"])
            if not user_info:
                self.logger.error(f"Failed to fetch user info for user_id={message.from_id}")
                return None

            vk_user = user_info[0]
            first_name = vk_user.first_name or "Unknown"
            last_name = vk_user.last_name or "Unknown"

            # Формируем данные пользователя
            user_data = {
                "bot_id": self.bot_id,
                "external_id": f"{message.from_id}",
                "first_name": first_name,
                "last_name": last_name
            }

            # Вызываем API для создания/получения пользователя
            response = await self.api_client.post("/users/get_or_create", data=user_data)
            if response and "user" in response:
                return response["user"]

            self.logger.error(f"Failed to create or retrieve user: {response}")
            return None

        except Exception as e:
            self.logger.error(f"Error while processing get_or_create_user: {e}", exc_info=True)
            return None

    async def get_last_user_action(self, user_id: int):
        params = {"user_id": user_id}
        response = await self.api_client.get("/statistics/last_action", params)
        
        if response and "last_action" in response:
            return response["last_action"]
        return None

    async def update_last_interaction(self, user_id: int):
        data = {"user_id": user_id}
        await self.api_client.post("/users/update_last_interaction", data)

    async def save_statistics(self, bot_id: int, user_id: int, action_type: str, message_text: str = None, category_id: int = None):
        data = {
            "bot_id": bot_id,
            "user_id": user_id,
            "action_type": action_type,
            "message_text": message_text,
            "category_id": category_id
        }
        await self.api_client.post("/statistics", data)

    async def get_answers(self, category_id: int):
        params = {"category_id": category_id}
        response = await self.api_client.get("/answers", params)
        return response.get("answers", [])

    async def get_categories(self, parent_id: int = None):
        params = {"bot_id": self.bot_id}
        if parent_id is not None:
            params["parent_id"] = parent_id
        response = await self.api_client.get("/categories", params)
        if response is None:
            self.logger.error(f"Failed to get categories for parent_id: {parent_id}")
            return []
        categories = response.get("categories", [])
        self.logger.info(f"Retrieved {len(categories)} categories for parent_id: {parent_id}")
        return categories

    async def get_category_by_name(self, name):
        params = {"name": name, "bot_id": self.bot_id}
        response = await self.api_client.get("/categories/search", params)
        if response is None:
            self.logger.error(f"Failed to get category by name: {name}")
            return None
        return response.get("category")
        
    async def get_category_by_id(self, category_id: int):
        params = {"category_id": category_id}
        response = await self.api_client.get(f"/categories/{category_id}", params)
        if response is None:
            self.logger.error(f"Failed to get category by ID: {category_id}")
            return None
        return response.get("category")

    async def start(self):
        """Запуск бота в отдельном потоке"""
        self.logger.info(f"Запуск бота {self.bot_id}")
        self.thread = threading.Thread(target=self.bot.run_forever, daemon=True)
        self.thread.start()


    def stop(self):
        """Остановка бота"""
        self.logger.info(f"Остановка бота {self.bot_id}")
        self.bot.loop_wrapper.stop()  # Останавливаем цикл
        if self.thread:
            self.thread.join()  # Ждем завершения потока

    def log_error(self, error: Exception, context: str = ""):
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
