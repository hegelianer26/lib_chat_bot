from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()
engine = create_engine("sqlite:///common_db.db2", echo=False)

SessionLocal = sessionmaker(bind=engine)

class Category(Base): 
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('category.id'), nullable=True)
    name = Column(String(200), nullable=False)

    parent = relationship(
        'Category',
        remote_side=[id],
        backref='children',
        lazy='joined'
    )


class Answer(Base): 
    __tablename__ = 'answer'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    text = Column(Text, nullable=False)
    image_path = Column(String)  # Новое поле для хранения пути к изображению

    category = relationship('Category', backref='answers')


class BotStatistics(Base):
    __tablename__ = 'bot_statistics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=True)
    action_type = Column(String(50), nullable=False)  # e.g. 'view_category', 'view_answer', 'menu'
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_text = Column(Text, nullable=True)



def init_db(database_url=None):
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    SessionLocal.configure(bind=engine)