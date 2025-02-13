from quart import Blueprint, jsonify, request, current_app

answers_bp = Blueprint('answers', __name__)

@answers_bp.route('/answers', methods=['GET'])
async def get_answers():
    category_id = request.args.get('category_id', type=int)

    if not category_id:
        return jsonify({"error": "Parameter 'category_id' is required"}), 400

    answer_repo = current_app.repositories["answer_repo"]
    answers = await answer_repo.get_answers_by_category_id(category_id)
    result = [answer.to_dict() for answer in answers]
    return jsonify({"answers": result}), 200