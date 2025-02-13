from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from bcrypt import hashpw, gensalt, checkpw
from cryptography.fernet import Fernet
import os
import enum
from sqlalchemy.sql import func
import pytz
import locale


try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Для Linux/Mac
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'russian')  # Для Windows

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Генерация ключа для шифрования токенов
SECRET_KEY = os.getenv('SECRET_KEY', Fernet.generate_key().decode())
cipher_suite = Fernet(SECRET_KEY.encode())

# Модель пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(60), nullable=False)
    organization_name = Column(String(200))
    group = Column(String(50))

    bots = relationship('ChatBot', back_populates='user')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password: str):
        self.password_hash = hashpw(password.encode(), gensalt()).decode()

    def check_password(self, password: str) -> bool:
        return checkpw(password.encode(), self.password_hash.encode())
    
    async def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'organization_name': self.organization_name,
            'group': self.group,
            'bots': [await bot.to_dict() for bot in self.bots]
        }

    @property
    def auth_id(self):
        return str(self.id)
    
    
# Модель чат-бота
class ChatBot(Base):
    __tablename__ = 'chat_bots'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)  # Название бота
    vk_token_encrypted = Column(String(500))  # Зашифрованный токен для ВКонтакте
    tg_token_encrypted = Column(String(500))  # Зашифрованный токен для Telegram
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Владелец бота

    # Связь с пользователем
    user = relationship('User', back_populates='bots')
    # Связь с настройками бота
    settings = relationship('BotSettings', uselist=False, back_populates='bot')
    # Связь с категориями бота
    categories = relationship('Category', back_populates='bot')

    statistics = relationship("BotStatistics", back_populates="bot")
    users = relationship("BotUser", back_populates="bot")

    async def set_vk_token(self, token: str):
        """Шифрование токена ВКонтакте."""
        self.vk_token_encrypted = cipher_suite.encrypt(token.encode()).decode()

    async def get_vk_token(self) -> str:
        """Дешифрование токена ВКонтакте."""
        return cipher_suite.decrypt(self.vk_token_encrypted.encode()).decode()

    async def set_tg_token(self, token: str):
        """Шифрование токена Telegram."""
        self.tg_token_encrypted = cipher_suite.encrypt(token.encode()).decode()

    async def get_tg_token(self) -> str:
        """Дешифрование токена Telegram."""
        return cipher_suite.decrypt(self.tg_token_encrypted.encode()).decode()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'settings': self.settings.to_dict() if self.settings else None,
            'categories': [category.to_dict() for category in self.categories]
        }

# Модель настроек бота
class BotSettings(Base):
    __tablename__ = 'bot_settings'
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('chat_bots.id'), unique=True, nullable=False)  # Связь с ботом
    welcome_message = Column(Text)  # Фраза приветствия
    help_message = Column(Text)  # Фраза помощи
    vk_button_color = Column(String(50))  # Цвет кнопок ВКонтакте
    tg_button_color = Column(String(50))  # Цвет кнопок Telegram
    is_active = Column(Boolean, default=True)  # Активен ли бот
    vk_is_active = Column(Boolean, default=False)  # Добавьте эту строку
    tg_is_active = Column(Boolean, default=False)  # Добавьте эту строку, если её ещё нет

    # Связь с ботом
    bot = relationship('ChatBot', back_populates='settings')

    def to_dict(self):
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'welcome_message': self.welcome_message,
            'help_message': self.help_message,
            'vk_button_color': self.vk_button_color,
            'tg_button_color': self.tg_button_color,
            'is_active': self.is_active
        }


# Модель категории (для ответов бота)
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)  # Название категории
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)  # Родительская категория
    bot_id = Column(Integer, ForeignKey('chat_bots.id'), nullable=False)  # Связь с ботом

    # Связь с родительской категорией
    parent = relationship(
        'Category',
        remote_side=[id],
        back_populates='children',
        lazy='joined'
    )
    # Связь с дочерними категориями
    children = relationship('Category', back_populates='parent', lazy="joined")
    # Связь с ботом
    bot = relationship('ChatBot', back_populates='categories')
    # Связь с ответами
    answers = relationship('Answer', back_populates='category', lazy="joined", cascade='all, delete-orphan')

    statistics = relationship("BotStatistics", back_populates="category")

    def to_dict(self, include_children=True, include_answers=True):
        data = {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'bot_id': self.bot_id,
        }
        
        if include_children and self.children:
            data['children'] = [child.to_dict(include_children=False, include_answers=False) for child in self.children]
        
        if include_answers and self.answers:
            data['answers'] = [answer.to_dict() for answer in self.answers]
        
        return data

# Модель ответа
class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)  # Текст ответа
    image_path = Column(String)  # Путь к изображению
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)  # Связь с категорией

    # Связь с категорией
    category = relationship('Category', back_populates='answers')

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'image_path': self.image_path,
            'category_id': self.category_id
        }


    
# Модель статистики бота
class BotStatistics(Base):
    __tablename__ = 'bot_statistics'
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('chat_bots.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('bot_users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    action_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    message_text = Column(Text, nullable=True)

    bot = relationship("ChatBot", back_populates="statistics")  # Добавлено это отношение
    user = relationship("BotUser", back_populates="statistics")
    category = relationship("Category", back_populates="statistics")

    async def to_dict(self):
        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'timestamp': self.timestamp.isoformat(),
            'message_text': self.message_text
        }

    
    
class UserSource(enum.Enum):
    VK = "vk"
    TELEGRAM = "telegram"

class BotUser(Base):
    __tablename__ = 'bot_users'
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey('chat_bots.id'), nullable=False)
    external_id = Column(String(50), nullable=False)  # ID пользователя в VK или Telegram
    source = Column(Enum(UserSource), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=func.now())
    last_interaction = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    bot = relationship("ChatBot", back_populates="users")
    statistics = relationship("BotStatistics", back_populates="user")

    def to_dict(self):
        # Получаем локальное время сервера
        local_tz = pytz.timezone('Europe/Moscow')  # Замените на ваш часовой пояс

        def format_datetime(dt):
            if dt:
                local_dt = dt.astimezone(local_tz)
                return local_dt.strftime('%d %B %Y, %H:%M')  
            return None

        return {
            'id': self.id,
            'bot_id': self.bot_id,
            'external_id': self.external_id,
            'source': self.source.value if self.source else None,
            'first_name': self.first_name if self.first_name else "",
            'last_name': self.last_name if self.last_name else "",
            'username': self.username if self.username else "",
            'created_at': format_datetime(self.created_at),
            'last_interaction': format_datetime(self.last_interaction),
            'user_name': f"{self.first_name} {self.last_name}" if self.first_name or self.last_name else "Неизвестный пользователь"
        }