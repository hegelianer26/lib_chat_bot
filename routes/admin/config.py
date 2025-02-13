from quart import Blueprint, request, render_template, redirect, url_for, flash, current_app, jsonify
from quart_auth import login_required, current_user
from db.redis_repository import RedisRepository
import logging
from db.redis_db import get_redis

logger = logging.getLogger(__name__)

config_bp = Blueprint('config', __name__)


@config_bp.route('/bot/<int:bot_id>/config', methods=['GET'])
@login_required
async def bot_config(bot_id):
    logger.info(f"Начало конфигурации бота {bot_id}")
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_settings_repo = current_app.repositories['bot_settings_repo']

    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot:
        logger.error(f"Бот с ID {bot_id} не найден")
        await flash('Бот не найден', 'error')
        return redirect(url_for('bots.bots_list'))

    if bot.user_id != int(current_user.auth_id):  # Проверка прав доступа
        logger.error(f"Нет прав доступа к боту {bot_id} для пользователя {current_user.auth_id}")
        await flash('У вас нет прав доступа к этому боту', 'error')
        return redirect(url_for('bots.bots_list'))

    settings = await bot_settings_repo.get_settings_by_bot_id(bot_id)
    if not settings:
        logger.warning(f"Настройки для бота {bot_id} не найдены, создаем новые")
        settings = await bot_settings_repo.create_settings(bot_id)

    # Fetch the decrypted VK token
    vk_token_last_part = None
    if bot.vk_token_encrypted:
        try:
            vk_token_last_part = (await bot.get_vk_token())[-4:]
        except Exception as e:
            logger.error(f"Ошибка при получении VK токена для бота {bot_id}: {str(e)}")

    logger.info(f"Отображение страницы конфигурации для бота {bot_id}")
    return await render_template(
        'bot_config.html',
        bot=bot,
        settings=settings,
        vk_token_last_part=vk_token_last_part  # Pass the last part of the token
    )


@config_bp.route('/bot/<int:bot_id>/config/general', methods=['POST'])
@login_required
async def update_general_settings(bot_id):
    logger.info(f"Обновление общих настроек бота {bot_id}")
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_settings_repo = current_app.repositories['bot_settings_repo']

    # Проверка доступа к боту
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))

    form = await request.form
    bot_name = form.get('bot_name')
    welcome_message = form.get('welcome_message')
    help_message = form.get('help_message')

    try:
        # Обновление данных бота
        await chatbot_repo.update_bot(bot_id, name=bot_name)
        await bot_settings_repo.update_settings(
            bot_id,
            welcome_message=welcome_message,
            help_message=help_message
        )

        bot_data = {
            "id": bot_id,
            "name": bot_name,
            "welcome_message": welcome_message,
            "help_message": help_message,
            "user_id": int(current_user.auth_id)
        }
        await RedisRepository.save_bot(bot_id, bot_data)

        await flash('Общие настройки бота успешно сохранены', 'success')
    except Exception as e:
        logger.exception(f"Ошибка при сохранении общих настроек бота {bot_id}: {str(e)}")
        await flash(f'Произошла ошибка при сохранении общих настроек: {str(e)}', 'error')

    return redirect(url_for('config.bot_config', bot_id=bot_id))


@config_bp.route('/bot/<int:bot_id>/config/tg', methods=['POST'])
@login_required
async def update_tg_settings(bot_id):
    logger.info(f"Обновление настроек Telegram для бота {bot_id}")
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_settings_repo = current_app.repositories['bot_settings_repo']
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))

    form = await request.form
    tg_token = form.get('tg_token')
    tg_button_color = form.get('tg_button_color')
    tg_is_active = form.get('tg_is_active') == 'on'

    try:
        settings = await bot_settings_repo.get_settings_by_bot_id(bot_id)
        if settings:
            update_data = {
                'tg_button_color': tg_button_color,
                'tg_is_active': tg_is_active,
            }
            await bot_settings_repo.update_settings(bot_id, **update_data)
        else:
            await bot_settings_repo.create_settings(
                bot_id,
                tg_button_color=tg_button_color,
                tg_is_active=tg_is_active,
            )

        if tg_token:
            await bot.set_tg_token(tg_token)

        await flash('Настройки Telegram успешно сохранены', 'success')
    except Exception as e:
        logger.exception(f"Ошибка при сохранении настроек Telegram для бота {bot_id}: {str(e)}")
        await flash(f'Произошла ошибка при сохранении настроек Telegram: {str(e)}', 'error')

    return redirect(url_for('config.bot_config', bot_id=bot_id))


@config_bp.route('/bot/<int:bot_id>/config/vk', methods=['POST'])
@login_required
async def update_vk_settings(bot_id):
    logger.info(f"Начало обновления настроек VK для бота {bot_id}")
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_settings_repo = current_app.repositories['bot_settings_repo']
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    
    # Проверка прав доступа
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))
    
    form = await request.form
    vk_token = form.get('vk_token')
    vk_button_color = form.get('vk_button_color')
    vk_is_active = form.get('vk_is_active') == 'on'  # Получаем bool значение

    try:
        # Обновление настроек бота в базе данных
        settings = await bot_settings_repo.get_settings_by_bot_id(bot_id)
        if settings:
            update_data = {
                'vk_button_color': vk_button_color,
                'vk_is_active': vk_is_active,  # Сохраняем как bool в БД
            }
            await bot_settings_repo.update_settings(bot_id, **update_data)

        # Сохранение токена в объекте ChatBot
        if vk_token:
            await bot.set_vk_token(vk_token)
            await chatbot_repo.update_bot(bot_id, vk_token_encrypted=bot.vk_token_encrypted)

        # Обновление данных в Redis
        bot_data = await RedisRepository.get_bot(bot_id)
        bot_data.update({
            "vk_token": vk_token,
            "vk_button_color": vk_button_color,
            "vk_is_active": str(vk_is_active).lower(),  # Преобразуем bool в строку ("true" или "false")
            "has_vk": True,
        })
        await RedisRepository.save_bot(bot_id, bot_data)

        # Отправляем уведомление о изменении
        async with get_redis() as redis:  # Use the same Redis connection mechanism
            await redis.publish('bot_updates', bot_id)

        await flash('Настройки VK успешно сохранены', 'success')
    except Exception as e:
        logger.exception(f"Ошибка при сохранении настроек VK для бота {bot_id}: {str(e)}")
        await flash(f'Произошла ошибка при сохранении настроек VK: {str(e)}', 'error')

    return redirect(url_for('config.bot_config', bot_id=bot_id))

@config_bp.route('/start-vk-bot/<int:bot_id>', methods=["POST"])
@login_required
async def start_vk_bot(bot_id):
    if not hasattr(current_app, 'vk_service'):
        return jsonify({"status": "error", "message": "VK service is not available"}), 500

    try:
        await current_app.vk_service.start_bot(bot_id)
        return jsonify({"status": "success", "message": f"Бот ВКонтакте с ID {bot_id} запущен"}), 200
    except Exception as e:
        logger.exception(f"Ошибка при запуске бота ВКонтакте {bot_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400


@config_bp.route('/stop-vk-bot/<int:bot_id>', methods=["POST"])
@login_required
async def stop_vk_bot(bot_id):
    if not hasattr(current_app, 'vk_service'):
        return jsonify({"status": "error", "message": "VK service is not available"}), 500

    try:
        await current_app.vk_service.stop_bot(bot_id)
        return jsonify({"status": "success", "message": f"Бот ВКонтакте с ID {bot_id} остановлен"}), 200
    except Exception as e:
        logger.exception(f"Ошибка при остановке бота ВКонтакте {bot_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400


@config_bp.route('/toggle-vk-bot/<int:bot_id>/<string:action>', methods=["POST"])
@login_required
async def toggle_vk_bot(bot_id, action):
    activate = action.lower() == "activate"
    try:
        if hasattr(current_app, 'vk_service'):
            await current_app.vk_service.toggle_bot(bot_id, activate)
            status = "запущен" if activate else "остановлен"
            return jsonify({"status": "success", "message": f"Бот ВКонтакте с ID {bot_id} {status}"}), 200
        else:
            return jsonify({"status": "error", "message": "VK service is not available"}), 500
    except Exception as e:
        logger.exception(f"Ошибка при переключении состояния бота ВКонтакте {bot_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400


@config_bp.route('/get-active-vk-bots', methods=["GET"])
@login_required
async def get_active_vk_bots():
    if not hasattr(current_app, 'vk_service'):
        return jsonify({"status": "error", "message": "VK service is not available"}), 500

    active_bots = await current_app.vk_service.get_active_bots()
    return jsonify({"active_bots": active_bots}), 200


@config_bp.route('/bot/<int:bot_id>/restart', methods=['POST'])
@login_required
async def restart_bot(bot_id):
    logger.info(f"Попытка перезапуска бота {bot_id}")
    chatbot_repo = current_app.repositories['chatbot_repo']

    # Проверка доступа к боту
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))

    try:
        if hasattr(current_app, 'bot_manager') and hasattr(current_app.bot_manager, 'restart_bot'):
            await current_app.bot_manager.restart_bot(bot_id)
            await flash('Бот успешно перезапущен', 'success')
        else:
            logger.warning(f"Метод restart_bot не найден для бота {bot_id}")
            await flash('Невозможно перезапустить бота: метод не найден', 'error')
    except Exception as e:
        logger.exception(f"Ошибка при перезапуске бота {bot_id}: {str(e)}")
        await flash(f'Произошла ошибка при перезапуске бота: {str(e)}', 'error')

    return redirect(url_for('config.bot_config', bot_id=bot_id))


@config_bp.route('/bot/<int:bot_id>/delete', methods=['POST'])
@login_required
async def delete_bot(bot_id):
    logger.info(f"Попытка удаления бота {bot_id}")
    chatbot_repo = current_app.repositories['chatbot_repo']

    # Проверка доступа к боту
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))

    try:
        await chatbot_repo.delete_bot(bot_id)
        
        await RedisRepository.delete_bot(bot_id)
        
        await flash('Бот успешно удален', 'success')
    except Exception as e:
        logger.exception(f"Ошибка при удалении бота {bot_id}: {str(e)}")
        await flash(f'Произошла ошибка при удалении бота: {str(e)}', 'error')

    return redirect(url_for('bots.bots_list'))

