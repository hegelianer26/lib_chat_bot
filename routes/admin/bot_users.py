from quart import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app
from quart_auth import login_required, current_user
from db.models import UserSource

bot_user_bp = Blueprint('bot_users', __name__)

@bot_user_bp.route('/<int:bot_id>/users')
@login_required
async def users_list(bot_id):
    # Получаем репозитории
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_user_repo = current_app.repositories['bot_user_repo']

    # Fetch the bot asynchronously
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return "Bot not found or access denied", 403
    
    return await render_template('users.html', bot=bot)

@bot_user_bp.route('/<int:bot_id>/users/filter', methods=['GET'])
@login_required
async def filter_users(bot_id):
    # Получаем репозитории
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_user_repo = current_app.repositories['bot_user_repo']

    # Fetch the bot asynchronously
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403

    # Get query parameters for filtering
    draw = int(request.args.get('draw', 1))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    search_value = request.args.get('search[value]', '').strip()
    order_column = int(request.args.get('order[0][column]', 0))
    order_dir = request.args.get('order[0][dir]', 'asc')
    source_filter = request.args.get('source')  # Фильтр по источнику (VK или Telegram)

    # Map order_column to actual column name
    columns = ['id', 'first_name', 'username', 'created_at', 'last_interaction']
    order_column_name = columns[order_column] if order_column < len(columns) else 'id'

    # Fetch filtered and paginated data
    total_records = await bot_user_repo.get_total_users_count(bot_id)
    filtered_records = await bot_user_repo.get_filtered_users_count(
        bot_id,
        search_value=search_value,
        source=source_filter
    )
    users = await bot_user_repo.get_paginated_users(
        bot_id,
        search_value=search_value,
        order_by=order_column_name,
        order_dir=order_dir,
        offset=start,
        limit=length,
        source=source_filter
    )

    # Prepare response
    data = [user.to_dict() for user in users]
    response = {
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    }

    return jsonify(response)

@bot_user_bp.route('/<int:bot_id>/users/<int:user_id>')
@login_required
async def user_details(bot_id, user_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_user_repo = current_app.repositories['bot_user_repo']
    
    # Fetch the bot asynchronously
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):  # Use current_user.auth_id without await
        await flash('Бот не найден или доступ запрещен', 'error')
        return redirect(url_for('bots.list_bots'))
    
    # Fetch the user details
    user = await bot_user_repo.get_user_by_id(user_id)
    if not user or user.bot_id != bot_id:
        await flash('Пользователь не найден', 'error')
        return redirect(url_for('bot_users.users_list', bot_id=bot_id))
    
    return await render_template('user_details.html', bot=bot, user=user)



@bot_user_bp.route('/<int:bot_id>/users/active')
@login_required
async def active_users(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_user_repo = current_app.repositories['bot_user_repo']
    
    # Fetch the bot asynchronously
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):  # Use current_user.auth_id without await
        return jsonify({'error': 'Бот не найден или доступ запрещен'}), 403
    
    # Get active users based on days parameter
    days = int(request.args.get('days', 30))
    users = await bot_user_repo.get_active_users(bot_id, days)
    
    return jsonify([user.to_dict() for user in users])
