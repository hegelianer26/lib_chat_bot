from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import logging
from config import Config
from .models import Base

logger = logging.getLogger(__name__)


DATABASE_URL = f"postgresql+asyncpg://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"

# Создание асинхронного движка
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,
    echo=True  # Set to False in production
)

# Создание асинхронной фабрики сессий
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Инициализация базы данных
async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Асинхронный контекстный менеджер для получения сессии базы данных
@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error occurred: {str(e)}")
            raise e
        finally:
            await session.close()

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
# import os
# from .models import Base

# load_dotenv()

# def get_engine():
#     database_url = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
#     return create_engine(database_url)

# engine = get_engine()
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def init_db(database_url=None):
#     if database_url:
#         new_engine = create_engine(database_url)
#         Base.metadata.create_all(new_engine)
#         SessionLocal.configure(bind=new_engine)
#     else:
#         Base.metadata.create_all(engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
