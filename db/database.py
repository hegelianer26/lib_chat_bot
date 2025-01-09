from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from .models import Base

load_dotenv()

def get_engine():
    database_url = os.getenv('DATABASE_URL', 'sqlite:///bot.db')
    return create_engine(database_url)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db(database_url=None):
    if database_url:
        new_engine = create_engine(database_url)
        Base.metadata.create_all(new_engine)
        SessionLocal.configure(bind=new_engine)
    else:
        Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
