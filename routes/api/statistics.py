from quart import Blueprint, jsonify, request, current_app

statistics_api_bp = Blueprint('bot_statistics', __name__)

@statistics_api_bp.route('/statistics', methods=['POST'])
async def save_statistics():
    data = await request.json
    required_fields = ['bot_id', 'user_id', 'action_type']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    statistics_repo = current_app.repositories["bot_statistics_repo"]
    await statistics_repo.save_statistics(
        bot_id=data['bot_id'],
        user_id=data['user_id'],
        action_type=data['action_type'],
        message_text=data.get('message_text'),
        category_id=data.get('category_id')
    )
    return jsonify({"status": "success", "message": "Статистика сохранена"}), 200

@statistics_api_bp.route('/statistics/last_action', methods=['GET'])
async def get_last_user_action():
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        return jsonify({"error": "Parameter 'user_id' is required"}), 400

    statistics_repo = current_app.repositories["bot_statistics_repo"]
    last_action = await statistics_repo.get_last_user_action(user_id)

    if not last_action:
        return jsonify({"last_action": None}), 200

    result = {
        "action_type": last_action.action_type,
        "timestamp": last_action.timestamp.isoformat()
    }
    return jsonify({"last_action": result}), 200