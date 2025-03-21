from quart import Blueprint, request, jsonify, render_template, current_app
from datetime import datetime, timedelta
from quart_auth import login_required, current_user

admin_stats_bp = Blueprint('statistics', __name__)

@admin_stats_bp.route('/bot/<int:bot_id>/statistics')
@login_required
async def statistics(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    return await render_template('statistics.html', bot=bot)

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/overview')
@login_required
async def get_statistics_overview(bot_id):
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    user_activity = await bot_statistics_repo.get_user_activity(bot_id, start_date, end_date)
    action_types = await bot_statistics_repo.get_message_text(bot_id, start_date, end_date)
    
    return jsonify({
        'user_activity': [
            {'user_id': user_id, 'actions': count}
            for user_id, count in user_activity
        ],
        'action_types': [
            {'action_type': action_type, 'count': count}
            for action_type, count in action_types
        ],
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
    })

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/daily')
@login_required
async def get_daily_statistics(bot_id):
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    daily_stats = await bot_statistics_repo.get_daily_statistics(bot_id, start_date, end_date)
    
    return jsonify({
        'daily_activity': [
            {
                'date': date.isoformat(),
                'count': count,
                'users_count': users_count
            }
            for date, count, users_count in daily_stats
        ]
    })

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/failed-queries')
@login_required
async def get_failed_queries_statistics(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    failed_queries = await bot_statistics_repo.get_failed_queries(bot_id)
    
    return jsonify({
        'queries': [
            {'query': text, 'count': count}
            for text, count in failed_queries
        ]
    })

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/messages')
@login_required
async def get_message_statistics(bot_id):
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    message_stats = await bot_statistics_repo.get_message_statistics(bot_id, start_date, end_date)
    
    return jsonify({
        'message_stats': [
            {
                'date': date.isoformat(),
                'message_count': count,
                'unique_users': users_count
            }
            for date, count, users_count in message_stats
        ]
    })

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/popular-actions')
@login_required
async def get_popular_actions(bot_id):
    limit = request.args.get('limit', 10, type=int)
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    popular_actions = await bot_statistics_repo.get_popular_actions(bot_id, limit)
    
    return jsonify({
        'popular_actions': [
            {'action_type': action_type, 'count': count}
            for action_type, count in popular_actions
        ]
    })

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/user-retention')
@login_required
async def get_user_retention(bot_id):
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    retention_data = await bot_statistics_repo.get_user_retention(bot_id, start_date, end_date)
    
    return jsonify({
        'user_retention': [
            {
                'date': date.isoformat(),
                'users_count': users_count
            }
            for date, users_count in retention_data
        ]
    })

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/category-usage')
@login_required
async def get_category_usage(bot_id):
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    category_usage = await bot_statistics_repo.get_category_usage(bot_id, start_date, end_date)
    
    return jsonify({
        'category_usage': [
            {
                'category_id': category_id,
                'count': count
            }
            for category_id, count in category_usage
        ]
    })

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/hourly-activity')
@login_required
async def get_hourly_activity(bot_id):
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    hourly_activity = await bot_statistics_repo.get_hourly_activity(bot_id, start_date, end_date)
    
    return jsonify({
        'hourly_activity': [
            {
                'hour': hour,
                'count': count
            }
            for hour, count in hourly_activity
        ]
    })

@admin_stats_bp.route('/bot/<int:bot_id>/api/statistics/average-session-duration')
@login_required
async def get_average_session_duration(bot_id):
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    bot_statistics_repo = current_app.repositories['bot_statistics_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        return jsonify({'error': 'Bot not found or access denied'}), 403
    
    avg_duration = await bot_statistics_repo.get_average_session_duration(bot_id, start_date, end_date)
    
    return jsonify({
        'average_session_duration': avg_duration.total_seconds() if avg_duration else None
    })