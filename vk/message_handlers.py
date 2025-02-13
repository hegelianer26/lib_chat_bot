from vkbottle.bot import Message
from vkbottle.dispatch.rules.base import PayloadContainsRule
from vkbottle import Keyboard, Text, KeyboardButtonColor
from services.vufind_service import search_catalog, format_catalog_record

class MessageHandlers:
    def __init__(self, vk_handler):
        self.vk_handler = vk_handler

    def setup(self):
        self.vk_handler.bot.on.message(PayloadContainsRule({"cmd": "catalog_search"}))(self.catalog_search_handler)
        self.vk_handler.bot.on.message(PayloadContainsRule({"cmd": "main_menu"}))(self.main_menu_handler)
        self.vk_handler.bot.on.message(PayloadContainsRule({"cmd": "go_back"}))(self.go_back_handler)
        self.vk_handler.bot.on.message(PayloadContainsRule({"cmd": "show_category"}))(self.show_category_handler)
        self.vk_handler.bot.on.message(text=["помощь", "help", "/help"])(self.help_handler)
        self.vk_handler.bot.on.message(text=["меню", "Меню"])(self.text_menu_handler)
        self.vk_handler.bot.on.message()(self.handle_message)

    async def handle_message(self, message: Message):
        if not self.vk_handler.is_active:
            self.vk_handler.logger.info(f"Ignoring message because bot with ID {self.vk_handler.bot_id} is inactive")
            return

        user = await self.vk_handler.get_or_create_user(message)
        if not user:
            self.vk_handler.logger.error(f"Failed to get or create user {message.from_id}")
            await message.answer("Произошла ошибка при обработке вашего запроса.")
            return
        
        last_action = await self.vk_handler.get_last_user_action(user['id'])
        if last_action and last_action.get('action_type') == 'catalog_search_start':
            await self.process_catalog_search(message)
            return
        
        await self.vk_handler.update_last_interaction(user['id'])
        await self.vk_handler.save_statistics(self.vk_handler.bot_id, user['id'], 'message_received', message.text)

        payload = message.get_payload_json()
        if payload:
            self.vk_handler.logger.debug(f"Received message with payload: {payload}")
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
            category = await self.vk_handler.get_category_by_name(message.text)
            if category:
                await self.show_category(message, category)
            else:
                keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
                await message.answer("Выберите категорию из меню:", keyboard=keyboard)

    async def help_handler(self, message: Message):
        self.vk_handler.logger.info("Help handler triggered")
        help_text = (
            "Доступные команды:\n"
            "🔍 Поиск в каталоге - для поиска в каталоге\n"
            "меню - вернуться в главное меню\n"
            "помощь - показать это сообщение\n"
            "Вы также можете вводить названия категорий для навигации."
        )
        keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
        await message.answer(help_text, keyboard=keyboard)

    async def catalog_search_handler(self, message: Message):
        user = await self.vk_handler.get_or_create_user(message)
        keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
        keyboard.add(Text("⬅ В главное меню", payload={"cmd": "main_menu"}), color=KeyboardButtonColor.SECONDARY)

        await self.vk_handler.save_statistics(self.vk_handler.bot_id, user['id'], 'catalog_search_start')
        await message.answer("Введите поисковый запрос для каталога:", keyboard=keyboard)

    async def main_menu_handler(self, message: Message):
        keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
        user = await self.vk_handler.get_or_create_user(message)
        await message.answer("Главное меню:", keyboard=keyboard)
        await self.vk_handler.save_statistics(self.vk_handler.bot_id, user['id'], 'main_menu')

    async def show_category_handler(self, message: Message):
        cat_id = message.get_payload_json().get("cat_id")
        current_path = message.get_payload_json().get("path", [])
        category = await self.vk_handler.get_category_by_id(cat_id)

        if not category:
            keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
            await message.answer("Категория не найдена", keyboard=keyboard)
            return

        await self.show_category(message, category, current_path)

    async def go_back_handler(self, message: Message):
        payload = message.get_payload_json()
        current_parent_id = payload.get("parent_id")
        current_path = payload.get("path", [])

        if not current_parent_id:
            keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
            await message.answer("Главное меню:", keyboard=keyboard)
            return

        target_cat = await self.vk_handler.get_category_by_id(current_parent_id)
        if not target_cat:
            keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
            await message.answer("Категория не найдена", keyboard=keyboard)
            return

        await self.show_category(message, target_cat, current_path)

    async def text_menu_handler(self, message: Message):
        keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
        await message.answer("Главное меню:", keyboard=keyboard)

    async def show_category(self, message: Message, category, current_path=None):
        if current_path is None:
            current_path = [category['name']]

        keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard(category['id'], current_path)
        answers = await self.vk_handler.get_answers(category['id'])

        user = await self.vk_handler.get_or_create_user(message)

        if answers:
            answer_text = "\n\n".join([answer['text'] for answer in answers])
            await message.answer(answer_text, keyboard=keyboard)
        else:
            await self.vk_handler.save_statistics(self.vk_handler.bot_id, user['id'], 'view_category', category_id=category['id'])
            await message.answer(f"Категория: {' > '.join(current_path)}", keyboard=keyboard)

        await self.vk_handler.save_statistics(self.vk_handler.bot_id, user['id'], 'view_category', category_id=category['id'])

    async def process_catalog_search(self, message: Message):
        user = await self.vk_handler.get_or_create_user(message)
        query = message.text.strip()

        if not query:
            await message.answer("Пожалуйста, введите поисковый запрос.")
            return

        data, catalog_url = await search_catalog(query)

        if data and 'records' in data:
            records = data['records']
            if records:
                response = "Результаты поиска:\n\n"
                for record in records[:5]:  # Показываем только первые 5 результатов
                    response += format_catalog_record(record) + "\n\n"
                response += f"\nПодробнее: {catalog_url}"
            else:
                response = "По вашему запросу ничего не найдено."
        else:
            response = "Произошла ошибка при поиске. Пожалуйста, попробуйте позже."

        keyboard = await self.vk_handler.keyboard_builder.build_categories_keyboard()
        await message.answer(response, keyboard=keyboard)
        await self.vk_handler.save_statistics(self.vk_handler.bot_id, user['id'], 'catalog_search_complete', message_text=query)