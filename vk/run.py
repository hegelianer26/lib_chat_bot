import sys
import logging
from vkbottle.bot import Bot
from vk_handler import VKHandler  # Путь к вашему файлу с VKHandler

logging.basicConfig(level=logging.DEBUG)

def main():
    bot_token = "vk1.a.KS_I-q0k87tNkJAK7jIxSswDftL2UqNjksACcDtHwN_oC4tftQkkporOE3y37o-C4IVdHpDchTgYy1nCydN47uqg70WXyCsR0z-RuagLWet8kipA9OLTQ9qjvKRxQzfkJMtsWj3GYvQ14-rT9rni583nHYQT0PicKglCA3k37u8TQdKlqVW8s5nz-ulpV60aRvqRHZnknXjZ6JVIxlLw6Q"  # Замените на ваш токен бота
    bot_id = 1  # Замените на ваш bot_id
    api_url = "http://0.0.0.0:8003/api"  # URL вашего API
    upload_dir = "uploads"  # Директория для загрузок

    bot = Bot(token=bot_token)
    vk_handler = VKHandler(bot, bot_id, api_url, upload_dir)

    if len(sys.argv) < 2:
        print("Usage: python manage_vk_handler.py <start|stop|update>")
        return

    command = sys.argv[1].lower()

    if command == "start":
        vk_handler.start()
    elif command == "stop":
        vk_handler.stop()
        
    elif command == "update":
        # Пример обновления настроек
        settings = {
            # Добавьте настройки для обновления
        }
        asyncio.run(vk_handler.update_settings(settings))
    else:
        print("Invalid command. Use start, stop, or update.")

if __name__ == "__main__":
    main()