import logging
import asyncio
import aiohttp
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor, PhotoMessageUploader
from vkbottle.dispatch.rules.base import PayloadContainsRule
from services.vufind_service import search_catalog, format_catalog_record
import sys
import asyncio  

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class VKHandler:
    def __init__(self, bot: Bot, bot_id: int, api_url: str, upload_dir: str):
        self.logger = logging.getLogger(f"VKHandler_{bot_id}")
        self.bot = bot
        self.bot_id = bot_id
        self.api_url = api_url
        self.upload_dir = upload_dir
        self.polling_task = None
        self.is_active = True
        self.loop = asyncio.get_event_loop()
        self.setup_handlers()

        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.logger.info(f"VKHandler initialized for bot ID: {bot_id}")

    def setup_handlers(self):
        
        self.logger.info("Setting up message handlers")
        # Регистрация обработчиков с использованием PayloadContainsRule
        self.bot.on.message(PayloadContainsRule({"cmd": "catalog_search"}))(self.catalog_search_handler)
        self.bot.on.message(PayloadContainsRule({"cmd": "main_menu"}))(self.main_menu_handler)
        self.bot.on.message(PayloadContainsRule({"cmd": "go_back"}))(self.go_back_handler)
        self.bot.on.message(PayloadContainsRule({"cmd": "show_category"}))(self.show_category_handler)

        # Регистрация обработчиков с фильтрами по тексту
        self.bot.on.message(text=["помощь", "help", "/help"])(self.help_handler)
        self.bot.on.message(text=["меню", "Меню"])(self.text_menu_handler)

        # Обработчик для остальных сообщений (общий)
        self.bot.on.message()(self.handle_message)

        self.logger.info("Message handlers set up successfully")


    async def api_post(self, endpoint: str, data: dict):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.api_url}{endpoint}", json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"API request failed: {response.status}, {await response.text()}")
                        return None
            except aiohttp.ClientError as e:
                self.logger.error(f"API request error: {str(e)}")
                return None

    async def api_get(self, endpoint: str, params: dict = None):
        self.logger.debug(f"API GET request: {self.api_url}{endpoint}, params: {params}")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.api_url}{endpoint}", params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.debug(f"API response: {result}")
                        return result
                    elif response.status == 404:
                        self.logger.warning(f"Resource not found at {endpoint}")
                        return None
                    else:
                        self.logger.error(f"API request failed: {response.status}")
                        return None
            except aiohttp.ClientError as e:
                self.logger.error(f"API request error: {str(e)}")
                return None

    async def get_or_create_user(self, message: Message):
        user_data = {
            "bot_id": self.bot_id,
            "external_id": f"vk_{message.from_id}",
            "first_name": message.from_id,  # Вы можете получить это из VK API, если нужно
            "last_name": None  # Аналогично first_name
        }
        
        user = await self.api_post("/users/get_or_create", data=user_data)
        if user and "user" in user:
            return user["user"]
        return None

    async def get_last_user_action(self, user_id: int):
        params = {"user_id": user_id}
        response = await self.api_get("/statistics/last_action", params)
        
        if response and "last_action" in response:
            return response["last_action"]
        return None


    async def update_last_interaction(self, user_id: int):
        data = {"user_id": user_id}
        await self.api_post("/users/update_last_interaction", data)

    async def save_statistics(self, bot_id: int, user_id: int, action_type: str, message_text: str = None, category_id: int = None):
        data = {
            "bot_id": bot_id,
            "user_id": user_id,
            "action_type": action_type,
            "message_text": message_text,
            "category_id": category_id
        }
        await self.api_post("/statistics", data)

    async def get_answers(self, category_id: int):
        params = {"category_id": category_id}
        response = await self.api_get("/answers", params)
        return response.get("answers", [])

    async def get_categories(self, parent_id: int = None):
        params = {"bot_id": self.bot_id}
        if parent_id is not None:
            params["parent_id"] = parent_id
        response = await self.api_get("/categories", params)
        if response is None:
            self.logger.error(f"Failed to get categories for parent_id: {parent_id}")
            return []
        categories = response.get("categories", [])
        self.logger.info(f"Retrieved {len(categories)} categories for parent_id: {parent_id}")
        return categories

    
    async def get_category_by_name(self, name):
        params = {"name": name, "bot_id": self.bot_id}
        response = await self.api_get("/categories/search", params)
        if response is None:
            self.logger.error(f"Failed to get category by name: {name}")
            return None
        return response.get("category")
        
    async def get_category_by_id(self, category_id: int):
        params = {"category_id": category_id}
        response = await self.api_get(f"/categories/{category_id}", params)
        if response is None:
            self.logger.error(f"Failed to get category by ID: {category_id}")
            return None
        return response.get("category")

    async def handle_message(self, message: Message):
        self.logger.info(f"Handling message: {message.text}")
        
        if not self.is_active:
            self.logger.info(f"Ignoring message because bot with ID {self.bot_id} is inactive")
            return

        user = await self.get_or_create_user(message)
        if not user:
            self.logger.error(f"Failed to get or create user {message.from_id}")
            await message.answer("Произошла ошибка при обработке вашего запроса.")
            return
        
        last_action = await self.get_last_user_action(user['id'])
        if last_action and last_action.get('action_type') == 'catalog_search_start':
            await self.process_catalog_search(message)
            return
        
        await self.update_last_interaction(user['id'])
        await self.save_statistics(self.bot_id, user['id'], 'message_received', message.text)

        payload = message.get_payload_json()
        if payload:
            self.logger.debug(f"Received message with payload: {payload}")
            if payload.get("cmd") == "show_category":
                await self.show_category_handler(message)
            elif payload.get("cmd") == "catalog_search":
                await self.catalog_search_handler(message)
            elif payload.get("cmd") == "main_menu":
                await self.main_menu_handler(message)
            elif payload.get("cmd") == "go_back":
                await self.go_back_handler(message)
        elif message.text == "🔍 Поиск в каталоге":
            await self.catalog_search_handler(message)
        else:
            category = await self.get_category_by_name(message.text)
            if category:
                await self.show_category(message, category)
            else:
                keyboard = await self.build_categories_keyboard()
                await message.answer("Выберите категорию из меню:", keyboard=keyboard)

    async def help_handler(self, message: Message):
        self.logger.info("Help handler triggered")
        help_text = (
            "Доступные команды:\n"
            "🔍 Поиск в каталоге - для поиска в каталоге\n"
            "меню - вернуться в главное меню\n"
            "помощь - показать это сообщение\n"
            "Вы также можете вводить названия категорий для навигации."
        )
        keyboard = await self.build_categories_keyboard()
        await message.answer(help_text, keyboard=keyboard)

    async def catalog_search_handler(self, message: Message):
        user = await self.get_or_create_user(message)

        keyboard = Keyboard(one_time=False, inline=False)
        keyboard.add(Text("⬅ В главное меню", payload={"cmd": "main_menu"}), color=KeyboardButtonColor.SECONDARY)

        await self.save_statistics(self.bot_id, user['id'], 'catalog_search_start')
        await message.answer("Введите поисковый запрос для каталога:", keyboard=keyboard)

    async def main_menu_handler(self, message: Message):
        keyboard = await self.build_categories_keyboard()

        user = await self.get_or_create_user(message)

        await message.answer("Главное меню:", keyboard=keyboard)
        await self.save_statistics(self.bot_id, user['id'], 'main_menu')

    async def show_category_handler(self, message: Message):
        cat_id = message.get_payload_json().get("cat_id")
        current_path = message.get_payload_json().get("path", [])
        category = await self.get_category_by_id(cat_id)

        if not category:
            keyboard = await self.build_categories_keyboard()
            await message.answer("Категория не найдена", keyboard=keyboard)
            return

        await self.show_category(message, category, current_path)


    async def go_back_handler(self, message: Message):
        payload = message.get_payload_json()
        current_parent_id = payload.get("parent_id")
        current_path = payload.get("path", [])

        if not current_parent_id:
            keyboard = await self.build_categories_keyboard()
            await message.answer("Главное меню:", keyboard=keyboard)
            return

        target_cat = await self.get_category_by_id(current_parent_id)
        if not target_cat:
            keyboard = await self.build_categories_keyboard()
            await message.answer("Категория не найдена", keyboard=keyboard)
            return

        await self.show_category(message, target_cat, current_path)

    async def text_menu_handler(self, message: Message):
        keyboard = await self.build_categories_keyboard()
        await message.answer("Главное меню:", keyboard=keyboard)
            
    async def build_categories_keyboard(self, parent_id=None, current_path=None):
        try:
            keyboard = Keyboard(one_time=False, inline=False)
            categories = await self.get_categories(parent_id)

            if not parent_id:
                # Добавляем кнопку "Поиск в каталоге" только в главном меню
                keyboard.add(
                    Text("🔍 Поиск в каталоге", payload={"cmd": "catalog_search"}),
                    color=KeyboardButtonColor.PRIMARY
                )
                keyboard.row()

            # Отображаем только корневые категории, если parent_id не указан
            if parent_id is None:
                categories = [cat for cat in categories if cat.get('parent_id') is None]

            short_cats = []
            long_cats = []

            # Разделяем категории на короткие и длинные названия
            for category in categories:
                if len(category['name']) <= 16:
                    short_cats.append(category)
                else:
                    long_cats.append(category)

            # Две колонки для коротких названий
            for i in range(0, len(short_cats), 2):
                row_cats = short_cats[i:i + 2]
                for cat in row_cats:
                    keyboard.add(
                        Text(
                            label=cat['name'],
                            payload={
                                "cmd": "show_category",
                                "cat_id": cat['id'],
                                "parent_id": parent_id if parent_id else 0,
                                "path": (current_path + [cat['name']]) if current_path else [cat['name']]
                            }
                        ),
                        color=KeyboardButtonColor.SECONDARY
                    )
                keyboard.row()

            # Одна колонка для длинных названий
            for cat in long_cats:
                keyboard.add(
                    Text(
                        label=cat['name'],
                        payload={
                            "cmd": "show_category",
                            "cat_id": cat['id'],
                            "parent_id": parent_id if parent_id else 0,
                            "path": (current_path + [cat['name']]) if current_path else [cat['name']]
                        }
                    ),
                    color=KeyboardButtonColor.SECONDARY
                )
                keyboard.row()

            # Добавляем кнопку "Назад" или "В главное меню"
            if parent_id:
                parent_category = await self.get_category_by_id(parent_id)
                if parent_category and parent_category.get('parent_id'):
                    keyboard.add(
                        Text(
                            label="⬅ Назад",
                            payload={
                                "cmd": "go_back",
                                "parent_id": parent_category['parent_id'],
                                "path": current_path[:-1] if current_path else None
                            }
                        ),
                        color=KeyboardButtonColor.PRIMARY
                    )
                else:
                    keyboard.add(
                        Text("⬅ В главное меню", payload={"cmd": "main_menu"}),
                        color=KeyboardButtonColor.PRIMARY
                    )
            return keyboard

        except Exception as e:
            self.logger.error(f"Ошибка при создании клавиатуры: {e}")
            keyboard = Keyboard(one_time=False, inline=False)
            keyboard.add(
                Text("⚠ Ошибка! В главное меню", payload={"cmd": "main_menu"}),
                color=KeyboardButtonColor.NEGATIVE
            )
            return keyboard
    
    async def process_catalog_search(self, message: Message):
        user = await self.get_or_create_user(message)
        data, catalog_url = search_catalog(message.text)

        keyboard = await self.build_categories_keyboard()

        if data and 'records' in data and data['records']:
            result_text = "🔍 Результаты поиска:\n\n"
            for record in data['records'][:5]:
                result_text += format_catalog_record(record) + "\n\n"

            count = data.get('resultCount', 0)
            result_text += f"Показано первых {min(len(data['records']), 5)} из {count}.\n"
            result_text += f"🌐 Ссылка на все результаты: {catalog_url}"

            await message.answer(result_text, keyboard=keyboard)
            await self.save_statistics(self.bot_id, user['id'], 'catalog_search_success', message_text=message.text)
        else:
            await message.answer("По вашему запросу ничего не найдено. Попробуйте уточнить запрос.", keyboard=keyboard)
            await self.save_statistics(self.bot_id, user['id'], 'catalog_search_unsuccess', message_text=message.text)


    async def show_category(self, message: Message, category, current_path=None):
        if current_path is None:
            current_path = [category['name']]

        keyboard = await self.build_categories_keyboard(category['id'], current_path)
        answers = await self.get_answers(category['id'])

        user = await self.get_or_create_user(message)

        if answers:
            answer_text = "\n\n".join([answer['text'] for answer in answers])

            image_path = None
            for answer in answers:
                if answer.get('image_path'):
                    full_image_path = answer['image_path']
                    self.logger.info(f"Checking image path: {full_image_path}")
                    if os.path.exists(full_image_path):
                        image_path = full_image_path
                        break
                    else:
                        self.logger.warning(f"Image file not found: {full_image_path}")

            if image_path:
                self.logger.info(f"Found image at path: {image_path}")
                try:
                    img = PhotoMessageUploader(self.bot.api)
                    attach = await img.upload(image_path)
                    self.logger.info(f"Image uploaded: {attach}")
                    await message.answer(answer_text, attachment=attach, keyboard=keyboard)
                except Exception as e:
                    self.logger.error(f"Error uploading image: {e}", exc_info=True)
                    await message.answer(answer_text, keyboard=keyboard)
            else:
                self.logger.info("No image found or image path does not exist.")
                await message.answer(answer_text, keyboard=keyboard)
        else:
            await self.save_statistics(self.bot_id, user['id'], 'view_category', category_id=category['id'])
            await message.answer(f"Категория: {' > '.join(current_path)}", keyboard=keyboard)

        await self.update_last_interaction(user['id'])

    async def send_error_message(self, message: Message, error_text: str):
        keyboard = await self.build_categories_keyboard()
        await message.answer(f"Произошла ошибка: {error_text}", keyboard=keyboard)

    def log_error(self, error: Exception, context: str = ""):
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)

    def start(self):
        self.bot.run_forever()

