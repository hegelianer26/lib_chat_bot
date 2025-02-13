from quart import Blueprint, jsonify, request, current_app

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
async def get_categories():
    parent_id = request.args.get('parent_id', type=int)
    bot_id = request.args.get('bot_id', type=int)

    if not bot_id:
        return jsonify({"error": "Parameter 'bot_id' is required"}), 400

    category_repo = current_app.repositories["category_repo"]
    categories = await category_repo.get_categories_by_parent_id(parent_id, bot_id)
    result = [category.to_dict(include_children=False) for category in categories]
    return jsonify({"categories": result}), 200

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
async def get_category_by_id(category_id):
    category_repo = current_app.repositories["category_repo"]
    category = await category_repo.get_category_by_id(int(category_id))

    if not category:
        return jsonify({"error": "Category not found"}), 404

    result = category.to_dict()
    return jsonify({"category": result}), 200

@categories_bp.route('/categories/search', methods=['GET'])
async def search_category_by_name():
    name = request.args.get('name')
    bot_id = request.args.get('bot_id', type=int)

    if not name or not bot_id:
        return jsonify({"error": "Parameters 'name' and 'bot_id' are required"}), 400

    category_repo = current_app.repositories["category_repo"]
    category = await category_repo.get_category_by_name(name, bot_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    result = category.to_dict()
    return jsonify({"category": result}), 200