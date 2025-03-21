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
    pool_size=20,
    max_overflow=60,
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
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()  # Commit changes if no exceptions occurred
    except SQLAlchemyError as e:
        await session.rollback()  # Rollback on error
        logger.error(f"Database error occurred: {str(e)}")
        raise e
    finally:
        await session.close()  # Ensure session is closed