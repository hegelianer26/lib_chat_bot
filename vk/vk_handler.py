# vk_handler.py

import logging
import asyncio
from vkbottle.bot import Bot
from api_client import APIClient
from message_handlers import MessageHandlers
from keyboard_builder import KeyboardBuilder

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
        self.loop = asyncio.get_event_loop()
        
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
        user_data = {
            "bot_id": self.bot_id,
            "external_id": f"vk_{message.from_id}",
            "first_name": message.from_id,
            "last_name": None
        }
        
        user = await self.api_client.post("/users/get_or_create", data=user_data)
        if user and "user" in user:
            return user["user"]
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

    def start(self):
        self.bot.run_forever()

    def log_error(self, error: Exception, context: str = ""):
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
