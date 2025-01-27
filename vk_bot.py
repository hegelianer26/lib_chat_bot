from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor
from vkbottle_types.events import GroupEventType, GroupTypes
import json
from vkbottle import PhotoMessageUploader
from dotenv import load_dotenv
import os
from db import service_standalone as db_service
from services.vufind_service import search_catalog, format_catalog_record
import logging

load_dotenv()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

token = os.getenv("VK_TOKEN")

bot = Bot(token=token)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'static')

def build_categories_keyboard(parent_id=None, current_path=None):
    try:
        keyboard = Keyboard(one_time=True, inline=False)
        categories = db_service.get_categories_by_parent_id(parent_id)
        if parent_id is None:
            keyboard.add(Text(
                label="🔍 Поиск в каталоге",
                payload={"cmd": "catalog_search"}
            ), color=KeyboardButtonColor.PRIMARY)
            keyboard.row()  

        short_cats = []
        long_cats = []
        
        for cat in categories:
            if len(cat.name) <= 16:
                short_cats.append(cat)
            else:
                long_cats.append(cat)

        # Two columns for short names
        for i in range(0, len(short_cats), 2):
            row_cats = short_cats[i:i + 2]
            for cat in row_cats:
                keyboard.add(Text(
                    label=cat.name,
                    payload={
                        "cmd": "show_category",
                        "cat_id": cat.id,
                        "parent_id": parent_id if parent_id else 0,
                        "path": current_path + [cat.name] if current_path else [cat.name]
                    }
                ), color=KeyboardButtonColor.SECONDARY)
            keyboard.row()

        # Single column for long names
        for cat in long_cats:
            keyboard.add(Text(
                label=cat.name,
                payload={
                    "cmd": "show_category",
                    "cat_id": cat.id,
                    "parent_id": parent_id if parent_id else 0,
                    "path": current_path + [cat.name] if current_path else [cat.name]
                }
            ), color=KeyboardButtonColor.SECONDARY)
            keyboard.row()

        if parent_id:
            parent_category = db_service.find_category_by_id(parent_id)
            if parent_category and parent_category.parent_id:
                keyboard.add(Text(
                    label="⬅ Назад",
                    payload={
                        "cmd": "go_back",
                        "parent_id": parent_category.parent_id,
                        "path": current_path[:-1] if current_path else None
                    }
                ), color=KeyboardButtonColor.SECONDARY)
            else:
                keyboard.add(Text(
                    label="⬅ В главное меню",
                    payload={"cmd": "main_menu"}
                ), color=KeyboardButtonColor.SECONDARY)

        return keyboard.get_json()
    except Exception as e:
        logger.error(f"[LOG] Ошибка при создании клавиатуры: {e}")
        keyboard = Keyboard(one_time=False, inline=False)
        keyboard.add(Text(
            label="⚠ Ошибка! В главное меню",
            payload={"cmd": "main_menu"}
        ), color=KeyboardButtonColor.NEGATIVE)
        return keyboard.get_json()



@bot.on.message(text=["помощь", "help", "/help"])
async def help_handler(message: Message):
    help_text = (
        "Доступные команды:\n"
        "🔍 Поиск в каталоге - для поиска в каталоге\n"
        "меню - вернуться в главное меню\n"
        "помощь - показать это сообщение\n"
        "Вы также можете вводить названия категорий для навигации."
    )
    keyboard = build_categories_keyboard(None)
    await message.answer(help_text, keyboard=keyboard)


@bot.on.raw_event(GroupEventType.MESSAGE_NEW)
async def debug_event(event: dict):
    try:
        message = event.get('object', {}).get('message', {})
        logger.info(f"[LOG] Received message: {message}")
    except Exception as e:
        logger.error(f"Error in debug_event: {e}", exc_info=True)

    # Если вам нужно больше информации о событии, вы можете логировать весь event
    logger.debug(f"[LOG] Full event: {event}")


@bot.on.message(payload={"cmd": "catalog_search"})
async def catalog_search_handler(message: Message):
    keyboard = Keyboard(one_time=True)
    keyboard.add(Text(
        label="⬅ В главное меню",
        payload={"cmd": "main_menu"}
    ), color=KeyboardButtonColor.SECONDARY)
    
    db_service.save_statistics(
        user_id=message.from_id,
        action_type='catalog_search_start'
    )

    await message.answer(
        "Введите поисковый запрос для каталога:",
        keyboard=keyboard.get_json()
    )


@bot.on.message(payload={"cmd": "main_menu"})
async def main_menu_handler(message: Message):
    print(f"[LOG] main_menu_handler triggered with message text: {message.text}, payload: {message.payload}")
    keyboard = build_categories_keyboard(None)
    await message.answer("Главное меню:", keyboard=keyboard)
    logger.info(f"[LOG] main_menu_handler completed")

    db_service.save_statistics(
        user_id=message.from_id,
        action_type='main_menu'
    )


@bot.on.message(payload={"cmd": "show_category"})
async def show_category_handler(message: Message):
    logger.info(f"[LOG] show_category_handler triggered with payload: {message.payload}")
    try:
        cat_id = message.payload["cat_id"]
        current_path = message.payload.get("path", [])
        cat = db_service.find_category_by_id(cat_id)

        if not cat:
            print(f"[LOG] Категория не найдена, cat_id: {cat_id}")
            keyboard = build_categories_keyboard(None)
            await message.answer("Категория не найдена", keyboard=keyboard)
            return

        answers = db_service.find_answers_by_cat_id(cat_id)
        
        if answers:
            answer_text = "\n\n".join([answer.text for answer in answers])
            keyboard = build_categories_keyboard(cat.parent_id, current_path[:-1])
            logger.info(f"[LOG] Sending answers for cat_id {cat_id}")
            await message.answer(
                answer_text,
                keyboard=keyboard,
            )
            return

        if cat.children:
            keyboard = build_categories_keyboard(cat.id, current_path)
            await message.answer(
                f"Категория: {' > '.join(current_path)}\nВыберите подкатегорию:", 
                keyboard=keyboard
            )
        else:
            keyboard = build_categories_keyboard(cat.parent_id, current_path[:-1])
            await message.answer(
                f"Категория: {' > '.join(current_path)}", 
                keyboard=keyboard
            )
        db_service.save_statistics(
            user_id=message.from_id,
            action_type='view_category',
            category_id=cat_id
        )
    except Exception as e:
        logger.error(f"[LOG] Ошибка в show_category_handler: {e}")
        keyboard = build_categories_keyboard(None)
        await message.answer("Произошла ошибка", keyboard=keyboard)


@bot.on.message(payload_map={"cmd": "go_back"})
async def go_back_handler(message: Message):
    print(f"[LOG] go_back_handler triggered with payload: {message.payload}")
    try:
        payload = json.loads(message.payload) if isinstance(message.payload, str) else message.payload
        logger.info(f"[LOG] Parsed payload: {payload}")
        
        current_parent_id = payload.get("parent_id")
        current_path = payload.get("path", [])
        
        logger.info(f"[LOG] Parent ID: {current_parent_id}, Path: {current_path}")
        
        if not current_parent_id:
            keyboard = build_categories_keyboard(None)
            await message.answer("Главное меню:", keyboard=keyboard)
            return

        target_cat = db_service.find_category_by_id(current_parent_id)
        if not target_cat:
            keyboard = build_categories_keyboard(None)
            await message.answer("Категория не найдена", keyboard=keyboard)
            return

        keyboard = build_categories_keyboard(target_cat.id, current_path)
        answers = db_service.find_answers_by_cat_id(target_cat.id)
        if answers:
            answer_text = "\n\n".join([a.text for a in answers])
            await message.answer(answer_text, keyboard=keyboard)
        else:
            await message.answer(
                f"Категория: {target_cat.name}",
                keyboard=keyboard
            )

    except json.JSONDecodeError as e:
        logger.error(f"[LOG] JSON parse error: {e}")
        keyboard = build_categories_keyboard(None)
        await message.answer("Ошибка обработки команды", keyboard=keyboard)
    except Exception as e:

        logger.error(f"[LOG] Ошибка в go_back_handler: {e}")
        logger.error(f"[LOG] Тип payload: {type(message.payload)}")
        logger.error(f"[LOG] Значение payload: {message.payload}")

        keyboard = build_categories_keyboard(None)
        await message.answer("Произошла ошибка", keyboard=keyboard)
    finally:
        logger.info("[LOG] go_back_handler completed")


@bot.on.message(text=["меню", "Меню"])
async def text_menu_handler(message: Message):
    logger.info("[LOG] text_menu_handler triggered")
    keyboard = build_categories_keyboard(None)
    await message.answer("Главное меню:", keyboard=keyboard)
    logger.info("[LOG] text_menu_handler completed")


@bot.on.message()
async def default_handler(message: Message):
    logger.info(f"[LOG] default_handler triggered with message text: {message.text}, payload: {message.payload}")
    # Check if user is in "catalog_search_start" mode
    last_action = db_service.get_last_user_action(message.from_id)
    if last_action and last_action.action_type == 'catalog_search_start':
        data, catalog_url = search_catalog(message.text)
        keyboard = build_categories_keyboard(None)
        if data and 'records' in data and data['records']:
            result_text = "🔍 Результаты поиска:\n\n"
            for record in data['records'][:5]:
                result_text += format_catalog_record(record) + "\n\n"

            count = data.get('resultCount', 0)
            result_text += f"Показано первых {min(len(data['records']), 5)} из {count}.\n"
            result_text += f"🌐 Ссылка на все результаты: {catalog_url}"

            await message.answer(result_text, keyboard=keyboard)
            db_service.save_statistics(
                user_id=message.from_id,
                action_type='catalog_search_success',
                message_text=message.text
            )
        else:
            await message.answer(
                "По вашему запросу ничего не найдено. Попробуйте уточнить запрос.",
                keyboard=keyboard
            )
        return

    if message.text:
        category = db_service.find_category_by_name(message.text)
        if category:
            keyboard = build_categories_keyboard(category.id, [category.name])
            logger.info(f"[LOG] Found category: {category.name} (id: {category.id})")
            answers = db_service.find_answers_by_cat_id(category.id)

            if answers:
                answer_text = "\n\n".join([answer.text for answer in answers])
                
                # Attempt to find an image
                image_path = None
                for answer in answers:
                    if answer.image_path:
                        full_image_path = os.path.join(UPLOAD_DIR, answer.image_path)
                        if os.path.exists(full_image_path):
                            image_path = full_image_path
                            logger.info(f"[LOG] Found image for answer: {image_path}")
                            break
                        else:
                            logger.warning(f"[LOG] Image file not found: {full_image_path}")

                # If an image was found, upload and send
                if image_path:
                    img = PhotoMessageUploader(bot.api)
                    attach = await img.upload(image_path)
                    await message.answer(answer_text, attachment=attach, keyboard=keyboard)
                else:
                    await message.answer(answer_text, keyboard=keyboard)
            else:
                db_service.save_statistics(
                    user_id=message.from_id,
                    action_type='text_query',
                    message_text=message.text
                )
                await message.answer(
                    f"Категория: {category.name}",
                    keyboard=keyboard
                )
        else:
            db_service.save_failed_query(
                user_id=message.from_id,
                query_text=message.text
            )
            keyboard = build_categories_keyboard(None)
            await message.answer("Категория не найдена", keyboard=keyboard)
    logger.info("[LOG] default_handler completed")


if __name__ == '__main__':
    bot.run_forever()
