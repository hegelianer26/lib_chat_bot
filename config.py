import os
from dotenv import load_dotenv

load_dotenv()  # Это загрузит переменные из .env файла

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    VK_TOKEN = os.environ.get('VK_TOKEN')
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    VUFIND = os.environ.get('VUFIND')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    
    # Добавляем конфигурацию для базы данных
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')

    # Добавляем конфигурацию для Redis
    REDIS_HOST = os.environ.get('REDIS_HOST')
    REDIS_PORT = os.environ.get('REDIS_PORT')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

class DevelopmentConfig(Config):
    DEBUG = True
    QUART_AUTH_COOKIE_SECURE = False  # Отключаем secure cookies для dev-среды

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    # Можете добавить специфические настройки для тестирования