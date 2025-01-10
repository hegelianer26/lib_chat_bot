from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime


Base = declarative_base()

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

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'children': [child.to_dict() for child in self.children],
            'answers': [answer.to_dict() for answer in self.answers]
        }
    

class Answer(Base): 
    __tablename__ = 'answer'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    text = Column(Text, nullable=False)
    image_path = Column(String)  # Новое поле для хранения пути к изображению

    category = relationship('Category', backref='answers')

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'category_id': self.category_id,
            'image_path': self.image_path
        }
    
    
class BotStatistics(Base):
    __tablename__ = 'bot_statistics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=True)
    action_type = Column(String(50), nullable=False)  # e.g. 'view_category', 'view_answer', 'menu'
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_text = Column(Text, nullable=True)
