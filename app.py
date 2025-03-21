from quart import Quart, current_app
from dotenv import load_dotenv
from quart_auth import QuartAuth
from db.database import init_db, get_db
from db.redis_db import init_redis_pool
import logging
import asyncio
import signal
from hypercorn.config import Config
from hypercorn.asyncio import serve
from db.db_repositories import (
    UserRepository,
    ChatBotRepository,
    BotSettingsRepository,
    CategoryRepository,
    AnswerRepository,
    BotStatisticsRepository,
    BotUserRepository,
)
from contextlib import asynccontextmanager

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Включение детального логирования пула соединений SQLAlchemy
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)

# Создание приложения
async def create_app():
    app = Quart(__name__, template_folder="templates")
    app.config.from_object("config.DevelopmentConfig")  # Загрузка конфигурации

    # Инициализация Quart-Auth
    QuartAuth(app)

    # Обработчик глобальных ошибок
    @app.errorhandler(Exception)
    async def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return {"error": "Internal server error"}, 500

    # Инициализация базы данных
    @app.before_serving
    async def initialize_db():
        await init_db()
        logger.info("Database initialized.")

    @app.before_serving
    async def initialize_redis():
        app.redis_pool = await init_redis_pool()
        app.logger.info("Redis connection pool established.")

    @app.after_serving
    async def close_redis():
        await app.redis_pool.close()
        app.logger.info("Redis connection pool closed.")

    # Фабрика зависимостей
    @asynccontextmanager
    async def get_repositories():
        async with get_db() as session:
            repositories = {
                "user_repo": UserRepository(session),
                "chatbot_repo": ChatBotRepository(session),
                "bot_settings_repo": BotSettingsRepository(session),
                "category_repo": CategoryRepository(session),
                "answer_repo": AnswerRepository(session),
                "bot_statistics_repo": BotStatisticsRepository(session),
                "bot_user_repo": BotUserRepository(session),
            }
            try:
                yield repositories
            finally:
                # Сессия закрывается автоматически через get_db
                pass

    @app.before_request
    async def before_request():
        current_app.repositories = {}

        async with get_db() as session:
            repositories = {
                "user_repo": UserRepository(session),
                "chatbot_repo": ChatBotRepository(session),
                "bot_settings_repo": BotSettingsRepository(session),
                "category_repo": CategoryRepository(session),
                "answer_repo": AnswerRepository(session),
                "bot_statistics_repo": BotStatisticsRepository(session),
                "bot_user_repo": BotUserRepository(session),
            }
            current_app.repositories = repositories

    # Очистка ресурсов после запроса
    @app.after_request
    async def after_request(response):
        if hasattr(current_app, "db_session"):
            await current_app.db_session.close()
        return response

    # Регистрация blueprint'ов
    from routes.api.categories import categories_bp
    from routes.api.answers import answers_bp
    from routes.api.statistics import statistics_api_bp
    from routes.api.users import users_api_bp

    from routes.admin.dialogs import dialogs_bp
    from routes.admin.statistics import admin_stats_bp
    from routes.admin.users import users_bp
    from routes.admin.config import config_bp
    from routes.admin.bots import bots_bp
    from routes.admin.bot_users import bot_user_bp

    app.register_blueprint(categories_bp, url_prefix="/api")
    app.register_blueprint(answers_bp, url_prefix="/api")
    app.register_blueprint(statistics_api_bp, url_prefix="/api")
    app.register_blueprint(users_api_bp, url_prefix="/api")

    app.register_blueprint(dialogs_bp)
    app.register_blueprint(admin_stats_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(bots_bp)
    app.register_blueprint(bot_user_bp)

    return app

# Логика остановки приложения
async def shutdown(app):
    logger.info("Shutting down the application...")
    if hasattr(app, "redis_pool"):
        await app.redis_pool.close()
        logger.info("Redis connection pool closed.")
    logger.info("Application shutdown complete.")

# Главная функция
async def main():
    app = await create_app()

    # Конфигурация Hypercorn
    config = Config()
    config.bind = ["0.0.0.0:8000"]

    # Обработка сигналов для корректного завершения работы
    loop = asyncio.get_event_loop()
    shutdown_event = asyncio.Event()

    def signal_handler(sig):
        logger.info(f"Received signal {sig.name}. Initiating shutdown...")
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda sig=sig: signal_handler(sig))

    try:
        logger.info("Starting the server...")
        await serve(app, config, shutdown_trigger=shutdown_event.wait)
    except asyncio.CancelledError:
        logger.info("Server task was cancelled.")
    finally:
        await shutdown(app)

if __name__ == "__main__":
    asyncio.run(main())