from quart import Blueprint, render_template, request, redirect, url_for, flash, current_app
from quart_auth import current_user, login_required
from db.redis_repository import RedisRepository
import logging
bots_bp = Blueprint('bots', __name__
                    )
logger = logging.getLogger(__name__)

@bots_bp.route('/bots')
@login_required
async def bots_list():
    user_id = int(current_user.auth_id)
    chatbot_repo = current_app.repositories['chatbot_repo']
    bots = await chatbot_repo.get_bots_by_user_id(user_id)
    return await render_template('bots_list.html', bots=bots)

@bots_bp.route('/bot/create', methods=['GET', 'POST'])
@login_required
async def create_bot():
    if request.method == 'POST':
        form = await request.form
        name = form['bot_name']
        
        chatbot_repo = current_app.repositories["chatbot_repo"]
        try:
            new_bot = await chatbot_repo.create_bot(name=name, user_id=int(current_user.auth_id))

            # Сохранение в Redis
            bot_data = {
                "id": new_bot.id,
                "name": new_bot.name,
                "user_id": new_bot.user_id
            }
            await RedisRepository.save_bot(new_bot.id, bot_data)

            return redirect(url_for('bots.bot_detail', bot_id=new_bot.id))
        except Exception as e:
            logger.error(f"Ошибка при создании бота: {str(e)}")
    
    return redirect(url_for('bots.bots_list'))


@bots_bp.route('/bot/<int:bot_id>/delete', methods=['POST'])
@login_required
async def delete_bot(bot_id):
    chatbot_repo = current_app.repositories["chatbot_repo"]
    
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if bot and bot.user_id == int(current_user.auth_id):
        try:
            # Удаление настроек

            # Удаление бота из базы данных
            await chatbot_repo.delete_bot(bot_id)
            # Удаление бота из Redis
            await RedisRepository.delete_bot(bot_id)
            
        except Exception as e:
            logger.error(f"Ошибка при удалении бота {bot_id}: {str(e)}")
    else:

        await flash('Бот не найден или у вас нет прав на его удаление', 'error')
    
    return redirect(url_for('bots.bots_list'))


@bots_bp.route('/bot/<int:bot_id>')
@login_required
async def bot_detail(bot_id):
    print(f"Вызвана функция bot_detail с bot_id={bot_id}")  # Отладочный вывод
    
    # Получаем репозиторий из current_app.repositories
    chatbot_repo = current_app.repositories["chatbot_repo"]
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    
    if bot and bot.user_id == int(current_user.auth_id):
        return await render_template('bot_detail.html', bot=bot)
    
    return redirect(url_for('bots.bots_list'))


