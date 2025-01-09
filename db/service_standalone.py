from db.models import Category, Answer, BotStatistics
from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc
from sqlalchemy.sql.expression import distinct
from db.database import SessionLocal

def get_all_categories():
    return SessionLocal().query(Category).options(
        joinedload(Category.children),
        joinedload(Category.answers)
    ).all()

def get_all_answers():
    with SessionLocal() as session:
        return session.query(Answer).all()


def get_answer_by_id(answer_id):
    with SessionLocal() as session:
        return session.query(Answer).filter_by(id=answer_id).first()

def create_category(name, parent_id=None):
    with SessionLocal() as session:
        cat = Category(name=name, parent_id=parent_id)
        session.add(cat)
        session.commit()

def create_answer(category_id, text):
    with SessionLocal() as session:
        ans = Answer(category_id=category_id, text=text)
        session.add(ans)
        session.commit()

def delete_category(cat_id):
    """
    Удаляет категорию, её подкатегории и связанные ответы.
    """
    with SessionLocal() as session:
        cat_obj = session.query(Category).get(cat_id)
        if not cat_obj:
            return

        # Сначала удаляем все ответы в этой категории
        for ans in cat_obj.answers:
            session.delete(ans)

        # Рекурсивное удаление подкатегорий
        def delete_subcategories(cat):
            for subc in cat.children:
                for subans in subc.answers:
                    session.delete(subans)
                delete_subcategories(subc)
                session.delete(subc)

        delete_subcategories(cat_obj)
        session.delete(cat_obj)
        session.commit()

def delete_answer(ans_id):
    with SessionLocal() as session:
        ans_obj = session.query(Answer).get(ans_id)
        if ans_obj:
            session.delete(ans_obj)
            session.commit()

def find_category_by_name(name):
    with SessionLocal() as session:
        return session.query(Category).filter_by(name=name).first()

def find_category_by_id(cat_id):
    with SessionLocal() as session:
        return session.query(Category).get(cat_id)

def find_answers_by_cat_id(cat_id):
    with SessionLocal() as session:
        return session.query(Answer).filter_by(category_id=cat_id).all()

def get_categories_by_parent_id(parent_id):
    with SessionLocal() as session:
        return session.query(Category).filter_by(parent_id=parent_id).all()
    

def update_category_name(cat_id, new_name):
    with SessionLocal() as session:
        cat_obj = session.query(Category).get(cat_id)
        if cat_obj:
            cat_obj.name = new_name
            session.commit()

def update_answer_text(ans_id, new_text):
    with SessionLocal() as session:
        ans_obj = session.query(Answer).get(ans_id)
        if ans_obj:
            ans_obj.text = new_text
            session.commit()

def create_answer(category_id, text, image_path=None):
    with SessionLocal() as session:
        ans = Answer(
            category_id=category_id,
            text=text,
            image_path=image_path  # Новое поле
        )
        session.add(ans)
        session.commit()


def save_statistics(user_id, action_type, category_id=None, message_text=None):
    with SessionLocal() as session:
        stat = BotStatistics(
            user_id=user_id,
            category_id=category_id,
            action_type=action_type,
            message_text=message_text
        )
        session.add(stat)
        session.commit()

def get_statistics(from_date=None, to_date=None):
    with SessionLocal() as session:
        query = session.query(BotStatistics)
        if from_date:
            query = query.filter(BotStatistics.timestamp >= from_date)
        if to_date:
            query = query.filter(BotStatistics.timestamp <= to_date)
        return query.all()
    

# def get_popular_categories(from_date=None, to_date=None):
#     with SessionLocal() as session:
#         query = session.query(
#             BotStatistics.category_id,
#             func.count(BotStatistics.id).label('access_count')
#         ).filter(
#             BotStatistics.category_id.isnot(None)
#         ).group_by(
#             BotStatistics.category_id
#         ).order_by(
#             desc('access_count')
#         )
        
#         if from_date:
#             query = query.filter(BotStatistics.timestamp >= from_date)
#         if to_date:
#             query = query.filter(BotStatistics.timestamp <= to_date)
            
#         return query.all()


# def get_popular_categories(start_date, end_date):
#     with SessionLocal() as session:
#         category_counts = (
#             session.query(
#                 Category.id,
#                 Category.name,
#                 func.count(BotStatistics.id).label("access_count")
#             )
#             .join(
#                 BotStatistics,
#                 BotStatistics.category_id == Category.id
#             )
#             .filter(
#                 BotStatistics.timestamp >= start_date,
#                 BotStatistics.timestamp <= end_date
#             )
#             .group_by(Category.id, Category.name)
#             .order_by(desc("access_count"))
#             .all()
#         )
#     return category_counts


def get_user_activity(from_date=None, to_date=None):
    with SessionLocal() as session:
        query = session.query(
            BotStatistics.user_id,
            func.count(BotStatistics.id).label('action_count')
        ).group_by(
            BotStatistics.user_id
        ).order_by(
            desc('action_count')
        )
        
        if from_date:
            query = query.filter(BotStatistics.timestamp >= from_date)
        if to_date:
            query = query.filter(BotStatistics.timestamp <= to_date)
            
        return query.all()
    
def get_daily_statistics(start_date, end_date):
    with SessionLocal() as session:
        daily_stats = session.query(
            func.date(BotStatistics.timestamp).label('date'),
            func.count(BotStatistics.id).label('count')
        ).filter(
            BotStatistics.timestamp >= start_date,
            BotStatistics.timestamp <= end_date
        ).group_by(
            func.date(BotStatistics.timestamp)
        ).all()
        
        return daily_stats

def get_query_statistics(limit=10):
    with SessionLocal() as session:
        queries = session.query(
            BotStatistics.message_text,
            func.count(BotStatistics.id).label('count')
        ).filter(
            BotStatistics.action_type.in_(
                ["text_query", "catalog_search_success", "catalog_search_start"]
            ),
            BotStatistics.message_text.isnot(None)
        ).group_by(
            BotStatistics.message_text
        ).order_by(
            desc('count')
        ).limit(limit).all()
        
        return queries

# def get_category_statistics(start_date=None, end_date=None):
#     with SessionLocal() as session:
#         query = session.query(
#             Category.name,
#             func.count(BotStatistics.id).label('count')
#         ).join(
#             BotStatistics,
#             BotStatistics.category_id == Category.id
#         ).group_by(
#             Category.id,
#             Category.name
#         ).order_by(
#             desc('count')
#         )
        
#         if start_date:
#             query = query.filter(BotStatistics.timestamp >= start_date)
#         if end_date:
#             query = query.filter(BotStatistics.timestamp <= end_date)
            
#         return query.all()

def get_user_activity_statistics(start_date=None, end_date=None):
    with SessionLocal() as session:
        query = session.query(
            BotStatistics.user_id,
            func.count(BotStatistics.id).label('count')
        ).group_by(
            BotStatistics.user_id
        ).order_by(
            desc('count')
        )
        
        if start_date:
            query = query.filter(BotStatistics.timestamp >= start_date)
        if end_date:
            query = query.filter(BotStatistics.timestamp <= end_date)
            
        return query.all()


def save_failed_query(user_id, query_text):
    with SessionLocal() as session:
        stat = BotStatistics(
            user_id=user_id,
            action_type='failed_query',
            message_text=query_text
        )
        session.add(stat)
        session.commit()

def get_failed_queries():
    with SessionLocal() as session:
        failed_queries = session.query(
            BotStatistics.message_text,
            func.count(BotStatistics.id).label('count')
        ).filter(
            BotStatistics.action_type == 'failed_query'
        ).group_by(
            BotStatistics.message_text
        ).order_by(
            desc('count')
        ).all()
        return failed_queries

def get_daily_statistics(start_date, end_date):
    with SessionLocal() as session:
        daily_stats = session.query(
            func.date(BotStatistics.timestamp).label('date'),
            func.count(BotStatistics.id).label('count'),
            func.count(distinct(BotStatistics.user_id)).label('users_count')
        ).filter(
            BotStatistics.timestamp >= start_date,
            BotStatistics.timestamp <= end_date
        ).group_by(
            func.date(BotStatistics.timestamp)
        ).all()
        
        return daily_stats
    


import vk_api

def get_users_detailed_statistics():
    vk_token = 'vk1.a.W0vw0HM-535XGcE6fIFASzkf83ZILxvzbZS9nlHAsv8ZOFsbVAPoaxcvcbKOUNJaKktyoqSC7NmPDaaMpd5-tkv95XOyqZOCn9LN-vUrAN_6QP6hgIhSjOhkW3fjOfxPMQYqaMvhsyzU8ieaumF3iFO1a20omqpmtQpHV3FaB8sXochhWasGISdNc5lJVTaXF2kANrzrZKxi4C_hn81sGw'
    vk = vk_api.VkApi(token=vk_token)

    with SessionLocal() as db_session:
        users_stats = db_session.query(
            BotStatistics.user_id,
            func.count(BotStatistics.id).label('request_count'),
            func.min(BotStatistics.timestamp).label('first_seen'),
            func.max(BotStatistics.timestamp).label('last_seen')
        ).group_by(
            BotStatistics.user_id
        ).order_by(
            desc('request_count')
        ).all()
        
        # Получаем информацию о пользователях из VK API
        user_ids = [stat[0] for stat in users_stats]
        vk_users = vk.method('users.get', {
            'user_ids': user_ids,
            'fields': ['first_name', 'last_name', 'photo_50']
        })
        
        # Создаем словарь с данными пользователей
        vk_users_dict = {user['id']: user for user in vk_users}
        
        return [(
            stat.user_id,
            stat.request_count,
            vk_users_dict.get(stat.user_id),
            stat.first_seen,
            stat.last_seen
        ) for stat in users_stats]



def get_last_user_action(user_id):
    with SessionLocal() as session:
        return (
            session.query(BotStatistics)
            .filter(BotStatistics.user_id == user_id)
            .order_by(BotStatistics.timestamp.desc())
            .first()
        )


def update_answer(answer_id, new_text, new_image_path=None):
    with SessionLocal() as session:
        answer = session.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            answer.text = new_text
            if new_image_path:
                answer.image_path = new_image_path
            session.commit()




def update_answer_image_path(answer_id, new_image_path):
    with  SessionLocal() as session:
        answer = session.query(Answer).filter_by(id=answer_id).first()
        if answer:
            answer.image_path = new_image_path
            session.commit()