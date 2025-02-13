import logging
from concurrent.futures import ThreadPoolExecutor
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from sqlalchemy.orm import Session
import asyncio

from db.db_repositories import ChatBotRepository, BotSettingsRepository, CategoryRepository, AnswerRepository, BotStatisticsRepository, BotUserRepository

class BotStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_subcategory = State()

class TGHandler:
    def __init__(self, bot: Bot, bot_id: int, db_session: Session, upload_dir: str):
        self.bot = bot
        self.bot_id = bot_id
        self.db_session = db_session
        self.upload_dir = upload_dir
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.executor = ThreadPoolExecutor()

        self.chatbot_repo = ChatBotRepository(db_session)
        self.bot_settings_repo = BotSettingsRepository(db_session)
        self.category_repo = CategoryRepository(db_session)
        self.answer_repo = AnswerRepository(db_session)
        self.statistics_repo = BotStatisticsRepository(db_session)
        self.bot_user_repo = BotUserRepository(db_session)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    async def setup_handlers(self):
        self.dp.message.register(self.send_welcome, Command(commands=['start']))
        self.dp.message.register(self.process_category, BotStates.waiting_for_category)
        self.dp.message.register(self.process_subcategory, BotStates.waiting_for_subcategory)

    async def send_welcome(self, message: types.Message):
        user = self.bot_user_repo.get_user_by_external_id(self.bot_id, message.from_user.id, 'TELEGRAM')
        if not user:
            user = self.bot_user_repo.create_user(
                bot_id=self.bot_id,
                external_id=message.from_user.id,
                source='TELEGRAM',
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                username=message.from_user.username
            )
        
        bot_settings = self.bot_settings_repo.get_settings_by_bot_id(self.bot_id)
        welcome_message = bot_settings.welcome_message if bot_settings else "Добро пожаловать!"
        
        await message.reply(welcome_message)
        await self.send_main_menu(message)

    async def send_main_menu(self, message: types.Message):
        categories = self.category_repo.get_categories_by_bot_id(self.bot_id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category in categories:
            if not category.parent_id:  # Только корневые категории
                keyboard.add(types.KeyboardButton(category.name))
        await message.reply("Выберите категорию:", reply_markup=keyboard)
        await BotStates.waiting_for_category.set()

    async def process_category(self, message: types.Message, state: FSMContext):
        category = self.category_repo.get_category_by_name(message.text, self.bot_id)
        if category:
            subcategories = self.category_repo.get_categories_by_parent_id(category.id, self.bot_id)
            if subcategories:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for subcat in subcategories:
                    keyboard.add(types.KeyboardButton(subcat.name))
                await message.reply("Выберите подкатегорию:", reply_markup=keyboard)
                await BotStates.waiting_for_subcategory.set()
                await state.update_data(category_id=category.id)
            else:
                await self.send_answer(message, category.id)
                await state.finish()
        else:
            await message.reply("Категория не найдена. Попробуйте снова.")
            
    async def process_subcategory(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        parent_category_id = data.get('category_id')
        subcategory = self.category_repo.get_category_by_name(message.text, self.bot_id)
        if subcategory and subcategory.parent_id == parent_category_id:
            await self.send_answer(message, subcategory.id)
            await state.clear()
        else:
            await message.reply("Подкатегория не найдена. Пожалуйста, выберите из предложенных вариантов.")

    async def send_answer(self, message: types.Message, category_id: int):
        answers = self.answer_repo.get_answers_by_category_id(category_id)
        if answers:
            for answer in answers:
                await message.reply(answer.text)
                if answer.image_path:
                    with open(answer.image_path, 'rb') as photo:
                        await message.reply_photo(photo)
        else:
            await message.reply("К сожалению, ответ не найден.")
        self.statistics_repo.save_statistics(
            bot_id=self.bot_id,
            user_id=self.bot_user_repo.get_user_by_external_id(self.bot_id, message.from_user.id, 'TELEGRAM').id,
            action_type='get_answer',
            category_id=category_id,
            message_text=message.text
        )
        await self.send_main_menu(message)

    async def start_polling(self):
        self.logger.info("Starting Telegram bot polling")
        try:
            await self.dp.start_polling(self.bot, skip_updates=True)
        except Exception as e:
            self.logger.error(f"Error in Telegram bot polling: {str(e)}")
        finally:
            self.logger.info("Telegram bot polling stopped")

    async def start_polling_in_thread(self):
        loop = asyncio.get_event_loop()
        self.executor.submit(loop.run_until_complete, self.start_polling())

    async def stop_polling(self):
        self.logger.info("Stopping Telegram bot polling")
        if self.dp:
            self.dp.stop_polling()
            self.logger.info("Telegram bot polling stopped")