import os
from app import create_app, db
from app.models import Category, Answer  # Импортируйте все необходимые модели
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Создание экземпляра приложения
app = create_app()

# Функция для инициализации базы данных
def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created.")

# Команда для создания таблиц базы данных через CLI
@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Initialized the database.")

# Контекстный процессор для добавления глобальных переменных в шаблоны
@app.context_processor
def inject_env_vars():
    return dict(
        APP_NAME=os.getenv('APP_NAME', 'ChatBot Admin'),
        ENVIRONMENT=os.getenv('FLASK_ENV', 'development')
    )

if __name__ == '__main__':
    # Перед запуском Flask-приложения вызываем инициализацию таблиц
    init_db()
    
    # Запуск приложения
    app.run(
        host=os.getenv('FLASK_RUN_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_RUN_PORT', 5001)),
        debug=os.getenv('FLASK_DEBUG', 'True') == 'True'
    )