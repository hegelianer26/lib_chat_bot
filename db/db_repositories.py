from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, distinct, desc
from .models import User, ChatBot, BotSettings, Category, Answer, BotStatistics, BotUser, UserSource
import datetime
from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import selectinload
from sqlalchemy import func, select as sa_select
from sqlalchemy.orm import joinedload
from sqlalchemy import select, update, delete
from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy import and_
from typing import List

class BaseRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

class UserRepository(BaseRepository):
    async def create_user(self, user: User):
        self.db_session.add(user)
        await self.db_session.commit()
        return user

    async def get_user_by_id(self, user_id):
        result = await self.db_session.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email):
        result = await self.db_session.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def update_user(self, user_id, **kwargs):
        user = await self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.db_session.commit()
        return user

    async def delete_user(self, user_id):
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db_session.delete(user)
            await self.db_session.commit()

class ChatBotRepository(BaseRepository):
    async def create_bot(self, name, user_id, vk_token=None, tg_token=None):
        bot = ChatBot(name=name, user_id=user_id)
        if vk_token:
            bot.set_vk_token(vk_token)
        if tg_token:
            bot.set_tg_token(tg_token)
        self.db_session.add(bot)
        await self.db_session.commit()
        return bot

    async def get_bot_by_id(self, bot_id):
        result = await self.db_session.execute(select(ChatBot).filter(ChatBot.id == bot_id))
        return result.scalar_one_or_none()

    async def get_bots_by_user_id(self, user_id):
        result = await self.db_session.execute(select(ChatBot).filter(ChatBot.user_id == user_id))
        return result.scalars().all()

    async def update_bot(self, bot_id, **kwargs):
        bot = await self.get_bot_by_id(bot_id)
        if bot:
            for key, value in kwargs.items():
                if key in ['vk_token', 'tg_token']:
                    getattr(bot, f'set_{key}')(value)
                else:
                    setattr(bot, key, value)
            await self.db_session.commit()
        return bot

    async def delete_bot(self, bot_id):
        # Step 1: Fetch the bot by ID
        bot = await self.get_bot_by_id(bot_id)
        if not bot:
            # If the bot doesn't exist, return early or raise an exception
            return  # Or raise an exception if required

        try:
            # Step 2: Delete associated BotSettings
            await self.db_session.execute(
                delete(BotSettings).where(BotSettings.bot_id == bot_id)
            )

            await self.db_session.execute(
                delete(Answer).
                where(Answer.category_id.in_(
                    select(Category.id).where(Category.bot_id == bot_id)
                ))
            )

            await self.db_session.execute(
                delete(BotStatistics).where(BotStatistics.bot_id == bot_id)
            )            

            await self.db_session.execute(
                delete(BotUser).where(BotUser.bot_id == bot_id)
            )



            await self.db_session.execute(
                delete(Category).where(Category.bot_id == bot_id)
            )

            await self.db_session.delete(bot)

            await self.db_session.commit()

        except Exception as e:
            # Handle any exceptions that occur during the deletion process
            await self.db_session.rollback()  # Rollback in case of failure
            raise RuntimeError(f"Ошибка при удалении бота {bot_id}: {e}")

    async def get_active_bots(self):
        result = await self.db_session.execute(
            select(ChatBot).join(BotSettings).filter(BotSettings.is_active == True)
        )
        return result.scalars().all()

class BotSettingsRepository(BaseRepository):
    async def create_settings(self, bot_id, welcome_message=None, help_message=None, vk_button_color=None, tg_button_color=None, is_active=True):
        settings = BotSettings(
            bot_id=bot_id,
            welcome_message=welcome_message,
            help_message=help_message,
            vk_button_color=vk_button_color,
            tg_button_color=tg_button_color,
            is_active=is_active
        )
        self.db_session.add(settings)
        await self.db_session.commit()
        return settings

    async def get_settings_by_bot_id(self, bot_id):
        result = await self.db_session.execute(select(BotSettings).filter(BotSettings.bot_id == bot_id))
        return result.scalar_one_or_none()

    async def update_settings(self, bot_id: int, **kwargs):
        query = update(BotSettings).where(BotSettings.bot_id == bot_id).values(**kwargs)
        await self.db_session.execute(query)
        await self.db_session.commit()

    async def delete_settings(self, bot_id):
        settings = await self.get_settings_by_bot_id(bot_id)
        if settings:
            await self.db_session.delete(settings)
            await self.db_session.commit()

class CategoryRepository(BaseRepository):
    async def create_category(self, name, bot_id, parent_id=None):
        category = Category(name=name, bot_id=bot_id, parent_id=parent_id)
        self.db_session.add(category)
        await self.db_session.commit()
        return category

    async def get_category_by_id(self, category_id):
        query = (
            select(Category)
            .options(
                selectinload(Category.children),
                selectinload(Category.answers)
            )
            .filter(Category.id == category_id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_categories_by_bot_id(self, bot_id):
        result = await self.db_session.execute(
            select(Category)
            .filter(Category.bot_id == bot_id)
            .options(
                selectinload(Category.children),
                selectinload(Category.answers)
            )
            .order_by(Category.id)
        )
        # Ensure we return a list, even if no categories are found
        return result.unique().scalars().all() or []

    async def update_category(self, category_id, **kwargs):
        category = await self.get_category_by_id(category_id)
        if category:
            for key, value in kwargs.items():
                setattr(category, key, value)
            await self.db_session.commit()
        return category
    
    async def get_category_with_details(self, category_id):
        stmt = (select(Category)
                .where(Category.id == category_id)
                .options(selectinload(Category.children), selectinload(Category.answers)))
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_category(self, category_id):
        category = await self.get_category_with_details(category_id)
        if category:
            await self.db_session.delete(category)
            await self.db_session.commit()
            return True
        return False

    async def get_category_by_name(self, name, bot_id):
        query = select(Category).options(
            selectinload(Category.children),
            selectinload(Category.answers)
        ).filter(
            Category.name == name,
            Category.bot_id == bot_id
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_categories_by_parent_id(self, parent_id, bot_id):
        query = (
            select(Category)
            .options(
                selectinload(Category.children),
                selectinload(Category.answers)
            )
            .filter(
                or_(Category.parent_id == parent_id, parent_id is None),
                Category.bot_id == bot_id
            )
        )
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
class AnswerRepository(BaseRepository):
    async def create_answer(self, category_id, text, image_path=None):
        answer = Answer(category_id=category_id, text=text, image_path=image_path)
        self.db_session.add(answer)
        await self.db_session.commit()
        return answer

    async def get_answer_by_id(self, answer_id):
        stmt = select(Answer).where(Answer.id == answer_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_answers_by_category_id(self, category_id):
        result = await self.db_session.execute(select(Answer).filter(Answer.category_id == category_id))
        return result.scalars().all()

    async def get_answers_by_bot_id(self, bot_id):
        result = await self.db_session.execute(
            select(Answer).join(Category).filter(Category.bot_id == bot_id)
        )
        return result.scalars().all()

    async def update_answer(self, answer_id, **kwargs):
        answer = await self.get_answer_with_category(answer_id)
        if answer:
            for key, value in kwargs.items():
                setattr(answer, key, value)
            await self.db_session.commit()
        return answer

    async def delete_answer(self, answer_id):
        answer = await self.get_answer_with_category(answer_id)
        if answer:
            await self.db_session.delete(answer)
            await self.db_session.commit()

    async def get_answer_with_bot_id(self, answer_id):
        result = await self.db_session.execute(
            select(Answer, Category.bot_id).join(Category).filter(Answer.id == answer_id)
        )
        return result.first()
    
    async def get_answer_with_category(self, answer_id):
        stmt = select(Answer).options(joinedload(Answer.category)).where(Answer.id == answer_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()
        

class BotStatisticsRepository(BaseRepository):
    async def save_statistics(self, bot_id: int, user_id: int, action_type: str, category_id=None, message_text=None):
        user = await self.db_session.execute(select(BotUser).filter(BotUser.id == user_id))
        if not user.scalar_one_or_none():
            raise ValueError(f"User with id {user_id} does not exist")

        new_statistics = BotStatistics(
            bot_id=bot_id,
            user_id=user_id,
            category_id=category_id,
            action_type=action_type,
            timestamp=datetime.now(timezone.utc),
            message_text=message_text
        )
        self.db_session.add(new_statistics)
        await self.db_session.commit()

    async def get_daily_statistics(self, bot_id, start_date, end_date):
        result = await self.db_session.execute(
            select(
                func.date(BotStatistics.timestamp).label('date'),
                func.count(BotStatistics.id).label('count'),
                func.count(distinct(BotStatistics.user_id)).label('users_count')
            ).filter(
                BotStatistics.bot_id == bot_id,
                BotStatistics.timestamp >= start_date,
                BotStatistics.timestamp <= end_date
            ).group_by(
                func.date(BotStatistics.timestamp)
            )
        )
        return result.all()

    async def get_failed_queries(self, bot_id):
        result = await self.db_session.execute(
            select(
                BotStatistics.message_text,
                func.count(BotStatistics.id).label('count')
            ).filter(
                BotStatistics.bot_id == bot_id,
                BotStatistics.action_type == 'failed_query'
            ).group_by(
                BotStatistics.message_text
            ).order_by(
                desc('count')
            )
        )
        return result.all()

    async def get_user_activity(self, bot_id, start_date, end_date):
        result = await self.db_session.execute(
            select(
                BotStatistics.user_id,
                func.count(BotStatistics.id).label('count')
            ).filter(
                BotStatistics.bot_id == bot_id,
                BotStatistics.timestamp.between(start_date, end_date)
            ).group_by(BotStatistics.user_id)
        )
        return result.all()

    async def get_action_types(self, bot_id, start_date, end_date):
        result = await self.db_session.execute(
            select(
                BotStatistics.action_type,
                func.count(BotStatistics.id).label('count')
            ).filter(
                BotStatistics.bot_id == bot_id,
                BotStatistics.timestamp.between(start_date, end_date)
            ).group_by(BotStatistics.action_type)
        )
        return result.all()

    async def get_message_statistics(self, bot_id, start_date, end_date):
        result = await self.db_session.execute(
            select(
                func.date(BotStatistics.timestamp).label('date'),
                func.count(BotStatistics.id).label('count'),
                func.count(func.distinct(BotStatistics.user_id)).label('users_count')
            ).filter(
                BotStatistics.bot_id == bot_id,
                BotStatistics.timestamp.between(start_date, end_date),
                BotStatistics.message_text.isnot(None)
            ).group_by(func.date(BotStatistics.timestamp))
        )
        return result.all()

    async def get_popular_actions(self, bot_id, limit):
        result = await self.db_session.execute(
            select(
                BotStatistics.action_type,
                func.count(BotStatistics.id).label('count')
            ).filter(
                BotStatistics.bot_id == bot_id
            ).group_by(BotStatistics.action_type).order_by(func.count(BotStatistics.id).desc()).limit(limit)
        )
        return result.all()

    async def get_user_retention(self, bot_id, start_date, end_date):
        result = await self.db_session.execute(
            select(
                func.date(BotStatistics.timestamp).label('date'),
                func.count(distinct(BotStatistics.user_id)).label('users_count')
            ).filter(
                BotStatistics.bot_id == bot_id,
                BotStatistics.timestamp.between(start_date, end_date)
            ).group_by(func.date(BotStatistics.timestamp))
        )
        return result.all()

    async def get_category_usage(self, bot_id, start_date, end_date):
        result = await self.db_session.execute(
            select(
                BotStatistics.category_id,
                func.count(BotStatistics.id).label('count')
            ).filter(
                BotStatistics.bot_id == bot_id,
                BotStatistics.timestamp.between(start_date, end_date),
                BotStatistics.category_id.isnot(None)
            ).group_by(BotStatistics.category_id)
        )
        return result.all()

    async def get_hourly_activity(self, bot_id, start_date, end_date):
        result = await self.db_session.execute(
            select(
                func.extract('hour', BotStatistics.timestamp).label('hour'),
                func.count(BotStatistics.id).label('count')
            ).filter(
                BotStatistics.bot_id == bot_id,
                BotStatistics.timestamp.between(start_date, end_date)
            ).group_by(func.extract('hour', BotStatistics.timestamp))
        )
        return result.all()

    async def get_average_session_duration(self, bot_id, start_date, end_date):
        subquery = select(
            BotStatistics.user_id,
            func.date(BotStatistics.timestamp).label('date'),
            (func.max(BotStatistics.timestamp) - func.min(BotStatistics.timestamp)).label('duration')
        ).filter(
            BotStatistics.bot_id == bot_id,
            BotStatistics.timestamp.between(start_date, end_date)
        ).group_by(BotStatistics.user_id, func.date(BotStatistics.timestamp)).subquery()
        result = await self.db_session.execute(select(func.avg(subquery.c.duration)))
        return result.scalar()

    async def get_last_user_action(self, user_id):
        result = await self.db_session.execute(
            select(BotStatistics).filter(
                BotStatistics.user_id == user_id
            ).order_by(desc(BotStatistics.timestamp)).limit(1)
        )
        return result.scalar_one_or_none()

class BotUserRepository(BaseRepository):
    async def create_user(self, bot_id, external_id, source, first_name=None, last_name=None, username=None):
        if isinstance(source, str):
            source = UserSource.VK if source.lower() == 'vk' else UserSource.TELEGRAM
        
        user = BotUser(
            bot_id=bot_id,
            external_id=str(external_id),  # Преобразуем external_id в строку
            source=source,
            first_name=str(first_name) if first_name is not None else None,  # Убедимся, что first_name - строка или None
            last_name=last_name,
            username=username
        )
        self.db_session.add(user)
        await self.db_session.commit()
        return user

    async def get_user_by_id(self, user_id):
        result = await self.db_session.execute(select(BotUser).filter(BotUser.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_external_id(self, bot_id: int, external_id: int, source: str):
        result = await self.db_session.execute(
            select(BotUser).filter(
                BotUser.bot_id == bot_id,
                BotUser.external_id == str(external_id),
                BotUser.source == source
            )
        )
        return result.scalar_one_or_none()

    async def get_all_users(self, bot_id):
        result = await self.db_session.execute(select(BotUser).filter(BotUser.bot_id == bot_id))
        return result.scalars().all()

    async def update_user(self, user_id, **kwargs):
        user = await self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            await self.db_session.commit()
        return user

    async def update_last_interaction(self, user_id):
        user = await self.get_user_by_id(user_id)
        if user:
            user.last_interaction = datetime.now(timezone.utc)
            await self.db_session.commit()
        return user

    async def delete_user(self, user_id):
        user = await self.get_user_by_id(user_id)
        if user:
            await self.db_session.delete(user)
            await self.db_session.commit()

    async def get_users_count(self, bot_id):
        result = await self.db_session.execute(
            select(func.count(BotUser.id)).filter(BotUser.bot_id == bot_id)
        )
        return result.scalar()

    async def get_users_by_source(self, bot_id, source):
        result = await self.db_session.execute(
            select(BotUser).filter(BotUser.bot_id == bot_id, BotUser.source == source)
        )
        return result.scalars().all()

    async def get_active_users(self, bot_id, days=30):
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db_session.execute(
            select(BotUser).filter(
                BotUser.bot_id == bot_id,
                BotUser.last_interaction >= thirty_days_ago
            )
        )
        return result.scalars().all()
    
    async def get_or_create_user(self, bot_id, external_id, source, first_name=None, last_name=None, username=None):
        user = await self.get_user_by_external_id(bot_id, external_id, source)
        if not user:
            user = await self.create_user(bot_id, external_id, source, first_name, last_name, username)
        return user

    async def get_total_users_count(self, bot_id: int) -> int:
        result = await self.db_session.execute(
            select(func.count(BotUser.id)).filter(BotUser.bot_id == bot_id)
        )
        return result.scalar() or 0

    async def get_filtered_users_count(self, bot_id: int, search_value: str, source: str = None) -> int:
        query = select(func.count(BotUser.id)).filter(BotUser.bot_id == bot_id)

        # Применяем фильтр по поисковому запросу
        if search_value.strip():
            query = query.filter(
                or_(
                    BotUser.first_name.ilike(f"%{search_value}%"),
                    BotUser.username.ilike(f"%{search_value}%"),
                    BotUser.external_id.ilike(f"%{search_value}%")
                )
            )

        # Применяем фильтр по источнику
        if source:
            try:
                # Преобразуем строку в перечисление UserSource
                source_enum = UserSource[source.upper()]
                query = query.filter(BotUser.source == source_enum)
            except KeyError:
                # Если источник некорректный, игнорируем фильтр
                pass

        result = await self.db_session.execute(query)
        return result.scalar() or 0
    
    async def get_paginated_users(
        self,
        bot_id: int,
        search_value: str,
        order_by: str,
        order_dir: str,
        offset: int,
        limit: int,
        source: str = None
    ) -> List[BotUser]:
        query = select(BotUser).filter(BotUser.bot_id == bot_id)

        # Применяем фильтр по поисковому запросу
        if search_value.strip():
            query = query.filter(
                or_(
                    BotUser.first_name.ilike(f"%{search_value}%"),
                    BotUser.username.ilike(f"%{search_value}%"),
                    BotUser.external_id.ilike(f"%{search_value}%")
                )
            )

        # Применяем фильтр по источнику
        if source:
            try:
                # Преобразуем строку в перечисление UserSource
                source_enum = UserSource[source.upper()]
                query = query.filter(BotUser.source == source_enum)
            except KeyError:
                # Если источник некорректный, игнорируем фильтр
                pass

        # Применяем сортировку
        if order_by in ['id', 'first_name', 'username', 'created_at', 'last_interaction']:
            if order_dir == 'asc':
                query = query.order_by(getattr(BotUser, order_by).asc())
            elif order_dir == 'desc':
                query = query.order_by(getattr(BotUser, order_by).desc())

        # Применяем пагинацию
        query = query.offset(offset).limit(limit)

        result = await self.db_session.execute(query)
        return result.scalars().all()
# from sqlalchemy.orm import Session
# from .models import User, ChatBot, BotSettings, Category, Answer, BotStatistics, BotUser, UserSource
# from sqlalchemy import func, distinct, desc
# import datetime
# from datetime import timedelta, datetime, timezone


# class BaseRepository:
#     def __init__(self, db_session: Session):
#         self.db_session = db_session

# class UserRepository(BaseRepository):
#     def create_user(self, user: User):
#         self.db_session.add(user)
#         self.db_session.commit()
#         return user

#     def get_user_by_id(self, user_id):
#         return self.db_session.query(User).filter(User.id == user_id).first()

#     def get_user_by_email(self, email):
#         return self.db_session.query(User).filter(User.email == email).first()

#     def update_user(self, user_id, **kwargs):
#         user = self.db_session.query(User).filter(User.id == user_id).first()
#         if user:
#             for key, value in kwargs.items():
#                 setattr(user, key, value)
#             self.db_session.commit()
#         return user

#     def delete_user(self, user_id):
#         user = self.db_session.query(User).filter(User.id == user_id).first()
#         if user:
#             self.db_session.delete(user)
#             self.db_session.commit()

# class ChatBotRepository(BaseRepository):
#     def create_bot(self, name, user_id, vk_token=None, tg_token=None):
#         bot = ChatBot(name=name, user_id=user_id)
#         if vk_token:
#             bot.set_vk_token(vk_token)
#         if tg_token:
#             bot.set_tg_token(tg_token)
#         self.db_session.add(bot)
#         self.db_session.commit()
#         return bot

#     def get_bot_by_id(self, bot_id):
#         return self.db_session.query(ChatBot).filter(ChatBot.id == bot_id).first()

#     def get_bots_by_user_id(self, user_id):
#         return self.db_session.query(ChatBot).filter(ChatBot.user_id == user_id).all()

#     def update_bot(self, bot_id, **kwargs):
#         bot = self.db_session.query(ChatBot).filter(ChatBot.id == bot_id).first()
#         if bot:
#             for key, value in kwargs.items():
#                 if key in ['vk_token', 'tg_token']:
#                     getattr(bot, f'set_{key}')(value)
#                 else:
#                     setattr(bot, key, value)
#             self.db_session.commit()
#         return bot

#     def delete_bot(self, bot_id):
#         bot = self.db_session.query(ChatBot).filter(ChatBot.id == bot_id).first()
#         if bot:
#             # Сначала удалим связанные настройки
#             self.db_session.query(BotSettings).filter(BotSettings.bot_id == bot_id).delete()
#             # Затем удалим самого бота
#             self.db_session.delete(bot)
#             self.db_session.commit()

#     def get_active_bots(self):
#         return self.db_session.query(ChatBot).join(BotSettings).filter(BotSettings.is_active == True).all()


# class BotSettingsRepository(BaseRepository):

#     def create_settings(self, bot_id, welcome_message=None, help_message=None, vk_button_color=None, tg_button_color=None, is_active=True):
#         settings = BotSettings(
#             bot_id=bot_id,
#             welcome_message=welcome_message,
#             help_message=help_message,
#             vk_button_color=vk_button_color,
#             tg_button_color=tg_button_color,
#             is_active=is_active
#         )
#         self.db_session.add(settings)
#         self.db_session.commit()
#         return settings

#     def get_settings_by_bot_id(self, bot_id):
#         return self.db_session.query(BotSettings).filter(BotSettings.bot_id == bot_id).first()

#     def update_settings(self, bot_id, **kwargs):
#         settings = self.db_session.query(BotSettings).filter(BotSettings.bot_id == bot_id).first()
#         if settings:
#             for key, value in kwargs.items():
#                 setattr(settings, key, value)
#             self.db_session.commit()
#         return settings

#     def delete_settings(self, bot_id):
#         settings = self.db_session.query(BotSettings).filter(BotSettings.bot_id == bot_id).first()
#         if settings:
#             self.db_session.delete(settings)
#             self.db_session.commit()


# class CategoryRepository:
#     def __init__(self, db_session):
#         self.db_session = db_session

#     def create_category(self, name, bot_id, parent_id=None):
#         category = Category(name=name, bot_id=bot_id, parent_id=parent_id)
#         self.db_session.add(category)
#         self.db_session.commit()
#         return category

#     def get_category_by_id(self, category_id):
#         return self.db_session.query(Category).filter(Category.id == category_id).first()

#     def get_categories_by_bot_id(self, bot_id):
#         return self.db_session.query(Category).filter(Category.bot_id == bot_id).all()

#     def update_category(self, category_id, **kwargs):
#         category = self.db_session.query(Category).filter(Category.id == category_id).first()
#         if category:
#             for key, value in kwargs.items():
#                 setattr(category, key, value)
#             self.db_session.commit()
#         return category

#     def delete_category(self, category_id):
#         category = self.db_session.query(Category).filter(Category.id == category_id).first()
#         if category:
#             self.db_session.delete(category)
#             self.db_session.commit()
            
#     def get_category_by_name(self, name, bot_id):
#         return self.db_session.query(Category).filter(
#             Category.name == name,
#             Category.bot_id == bot_id
#         ).first()

#     def get_categories_by_parent_id(self, parent_id, bot_id):
#         return self.db_session.query(Category).filter(
#             Category.parent_id == parent_id,
#             Category.bot_id == bot_id
#         ).all()
    
    
# class AnswerRepository(BaseRepository):

#     def create_answer(self, category_id, text, image_path=None):
#         answer = Answer(category_id=category_id, text=text, image_path=image_path)
#         self.db_session.add(answer)
#         self.db_session.commit()
#         return answer

#     def get_answer_by_id(self, answer_id):
#         return self.db_session.query(Answer).filter(Answer.id == answer_id).first()

#     def get_answers_by_category_id(self, category_id):
#         return self.db_session.query(Answer).filter(Answer.category_id == category_id).all()

#     def get_answers_by_bot_id(self, bot_id):
#         return self.db_session.query(Answer).join(Category).filter(Category.bot_id == bot_id).all()

#     def update_answer(self, answer_id, **kwargs):
#         answer = self.db_session.query(Answer).filter(Answer.id == answer_id).first()
#         if answer:
#             for key, value in kwargs.items():
#                 setattr(answer, key, value)
#             self.db_session.commit()
#         return answer

#     def delete_answer(self, answer_id):
#         answer = self.db_session.query(Answer).filter(Answer.id == answer_id).first()
#         if answer:
#             self.db_session.delete(answer)
#             self.db_session.commit()

#     def get_answer_with_bot_id(self, answer_id):
#         return self.db_session.query(Answer, Category.bot_id).join(Category).filter(Answer.id == answer_id).first()

# class BotStatisticsRepository(BaseRepository):

#     def save_statistics(self, bot_id: int, user_id: int, action_type: str, category_id=None, message_text=None):
#         # Проверяем, существует ли пользователь
#         user = self.db_session.query(BotUser).filter(BotUser.id == user_id).first()
#         if not user:
#             raise ValueError(f"User with id {user_id} does not exist")

#         new_statistics = BotStatistics(
#             bot_id=bot_id,
#             user_id=user_id,  # Используем существующий user_id
#             category_id=category_id,
#             action_type=action_type,
#             timestamp=datetime.now(timezone.utc),
#             message_text=message_text
#         )
#         self.db_session.add(new_statistics)
#         self.db_session.commit()
    

#     def get_daily_statistics(self, bot_id, start_date, end_date):
#         daily_stats = self.db_session.query(
#             func.date(BotStatistics.timestamp).label('date'),
#             func.count(BotStatistics.id).label('count'),
#             func.count(distinct(BotStatistics.user_id)).label('users_count')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.timestamp >= start_date,
#             BotStatistics.timestamp <= end_date
#         ).group_by(
#             func.date(BotStatistics.timestamp)
#         ).all()
#         return daily_stats

#     def get_failed_queries(self, bot_id):
#         failed_queries = self.db_session.query(
#             BotStatistics.message_text,
#             func.count(BotStatistics.id).label('count')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.action_type == 'failed_query'
#         ).group_by(
#             BotStatistics.message_text
#         ).order_by(
#             desc('count')
#         ).all()
#         return failed_queries

#     def get_user_activity(self, bot_id, start_date, end_date):
#         return self.db_session.query(
#             BotStatistics.user_id,
#             func.count(BotStatistics.id).label('count')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.timestamp.between(start_date, end_date)
#         ).group_by(BotStatistics.user_id).all()

#     def get_action_types(self, bot_id, start_date, end_date):
#         return self.db_session.query(
#             BotStatistics.action_type,
#             func.count(BotStatistics.id).label('count')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.timestamp.between(start_date, end_date)
#         ).group_by(BotStatistics.action_type).all()

#     def get_message_statistics(self, bot_id, start_date, end_date):
#         return self.db_session.query(
#             func.date(BotStatistics.timestamp).label('date'),
#             func.count(BotStatistics.id).label('count'),
#             func.count(func.distinct(BotStatistics.user_id)).label('users_count')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.timestamp.between(start_date, end_date),
#             BotStatistics.message_text.isnot(None)
#         ).group_by(func.date(BotStatistics.timestamp)).all()

#     def get_popular_actions(self, bot_id, limit):
#         return self.db_session.query(
#             BotStatistics.action_type,
#             func.count(BotStatistics.id).label('count')
#         ).filter(
#             BotStatistics.bot_id == bot_id
#         ).group_by(BotStatistics.action_type).order_by(func.count(BotStatistics.id).desc()).limit(limit).all()

#     def get_user_retention(self, bot_id, start_date, end_date):
#         """
#         Получает статистику удержания пользователей.
#         """
#         return self.db_session.query(
#             func.date(BotStatistics.timestamp).label('date'),
#             func.count(distinct(BotStatistics.user_id)).label('users_count')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.timestamp.between(start_date, end_date)
#         ).group_by(func.date(BotStatistics.timestamp)).all()

#     def get_category_usage(self, bot_id, start_date, end_date):
#         """
#         Получает статистику использования категорий.
#         """
#         return self.db_session.query(
#             BotStatistics.category_id,
#             func.count(BotStatistics.id).label('count')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.timestamp.between(start_date, end_date),
#             BotStatistics.category_id.isnot(None)
#         ).group_by(BotStatistics.category_id).all()

#     def get_hourly_activity(self, bot_id, start_date, end_date):
#         """
#         Получает почасовую активность пользователей.
#         """
#         return self.db_session.query(
#             func.extract('hour', BotStatistics.timestamp).label('hour'),
#             func.count(BotStatistics.id).label('count')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.timestamp.between(start_date, end_date)
#         ).group_by(func.extract('hour', BotStatistics.timestamp)).all()

#     def get_average_session_duration(self, bot_id, start_date, end_date):
#         """
#         Получает среднюю продолжительность сессии пользователей.
#         """
#         subquery = self.db_session.query(
#             BotStatistics.user_id,
#             func.date(BotStatistics.timestamp).label('date'),
#             func.max(BotStatistics.timestamp) - func.min(BotStatistics.timestamp).label('duration')
#         ).filter(
#             BotStatistics.bot_id == bot_id,
#             BotStatistics.timestamp.between(start_date, end_date)
#         ).group_by(BotStatistics.user_id, func.date(BotStatistics.timestamp)).subquery()

#         return self.db_session.query(func.avg(subquery.c.duration)).scalar()
    
#     def get_last_user_action(self, user_id):
#         return self.db_session.query(BotStatistics).filter(
#             BotStatistics.user_id == user_id
#         ).order_by(desc(BotStatistics.timestamp)).first()

# class BotUserRepository(BaseRepository):
#     def create_user(self, bot_id, external_id, source, first_name=None, last_name=None, username=None):
#         # Преобразуем строковое значение source в соответствующее значение Enum
#         if isinstance(source, str):
#             source = UserSource.VK if source.lower() == 'vk' else UserSource.TELEGRAM
        
#         user = BotUser(
#             bot_id=bot_id,
#             external_id=str(external_id),
#             source=source,  # Теперь source - это значение Enum
#             first_name=first_name,
#             last_name=last_name,
#             username=username
#         )
#         self.db_session.add(user)
#         self.db_session.commit()
#         return user

#     def get_user_by_id(self, user_id):
#         return self.db_session.query(BotUser).filter(BotUser.id == user_id).first()

#     # def get_user_by_external_id(self, bot_id, external_id, source):
#     #     return self.db_session.query(BotUser).filter(
#     #         BotUser.bot_id == bot_id,
#     #         BotUser.external_id == external_id,
#     #         BotUser.source == source
#     #     ).first()
#     def get_user_by_external_id(self, bot_id: int, external_id: int, source: str):
#         return self.db_session.query(BotUser).filter(
#             BotUser.bot_id == bot_id,
#             BotUser.external_id == str(external_id),
#             BotUser.source == source
#         ).first()

#     def get_all_users(self, bot_id):
#         return self.db_session.query(BotUser).filter(BotUser.bot_id == bot_id).all()

#     def update_user(self, user_id, **kwargs):
#         user = self.db_session.query(BotUser).filter(BotUser.id == user_id).first()
#         if user:
#             for key, value in kwargs.items():
#                 setattr(user, key, value)
#             self.db_session.commit()
#         return user

#     def update_last_interaction(self, user_id):
#         user = self.db_session.query(BotUser).filter(BotUser.id == user_id).first()
#         if user:
#             user.last_interaction = datetime.now(timezone.utc)
#             self.db_session.commit()
#         return user

#     def delete_user(self, user_id):
#         user = self.db_session.query(BotUser).filter(BotUser.id == user_id).first()
#         if user:
#             self.db_session.delete(user)
#             self.db_session.commit()

#     def get_users_count(self, bot_id):
#         return self.db_session.query(func.count(BotUser.id)).filter(BotUser.bot_id == bot_id).scalar()

#     def get_users_by_source(self, bot_id, source):
#         return self.db_session.query(BotUser).filter(BotUser.bot_id == bot_id, BotUser.source == source).all()

#     def get_active_users(self, bot_id, days=30):
#         thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=days)
#         return self.db_session.query(BotUser).filter(
#             BotUser.bot_id == bot_id,
#             BotUser.last_interaction >= thirty_days_ago
#         ).all()