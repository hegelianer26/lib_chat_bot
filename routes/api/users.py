from quart import Blueprint, jsonify, request, current_app
from db.models import UserSource
import logging


logger = logging.getLogger(__name__)

users_api_bp = Blueprint('bots_users', __name__)



@users_api_bp.route('/users/get_or_create', methods=['POST'])
async def get_or_create_user():
    data = await request.json
    required_fields = ['bot_id', 'external_id']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    bot_id = data['bot_id']
    external_id = data['external_id']
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    bot_user_repo = current_app.repositories["bot_user_repo"]
    user = await bot_user_repo.get_or_create_user(
        bot_id=bot_id,
        external_id=external_id,
        source=UserSource.VK,
        first_name=first_name,
        last_name=last_name
    )
    return jsonify({"user": await user.to_dict()}), 200

@users_api_bp.route('/users/update_last_interaction', methods=['POST'])
async def update_last_interaction():
    try:
        data = await request.json
        required_fields = ['user_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        user_id = data['user_id']
        bot_user_repo = current_app.repositories["bot_user_repo"]

        # Проверяем существование пользователя
        user = await bot_user_repo.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User with id {user_id} not found")
            return jsonify({"error": "User not found"}), 404

        await bot_user_repo.update_last_interaction(user_id)
        logger.info(f"Updated last interaction for user {user_id}")
        return jsonify({"status": "success", "message": "Время взаимодействия обновлено"}), 200

    except Exception as e:
        logger.error(f"Error updating last interaction for user {user_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500