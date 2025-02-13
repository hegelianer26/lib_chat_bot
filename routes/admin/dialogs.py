from quart import Blueprint, request, render_template, redirect, url_for, flash, current_app
from utils.html_utils import clean_html_content
from utils.file_utils import generate_unique_filename
from werkzeug.utils import secure_filename
import os
from quart_auth import login_required, current_user
import logging
import asyncio

logger = logging.getLogger(__name__)
dialogs_bp = Blueprint('dialogs', __name__)



@dialogs_bp.route('/bot/<int:bot_id>/dialogs')
@login_required  # Ensure the user is authenticated
async def dialogs(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    
    # Fetch the bot asynchronously
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):  # Use await current_user.auth_id
        logger.error(f"Bot not found or access denied for bot ID {bot_id}")
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))
    
    category_repo = current_app.repositories['category_repo']
    answer_repo = current_app.repositories['answer_repo']
    
    # Fetch categories and answers asynchronously
    categories = await category_repo.get_categories_by_bot_id(bot_id)
    answers = await answer_repo.get_answers_by_bot_id(bot_id)
    
    # Filter root categories
    root_categories = [c for c in categories if c.parent_id is None]
    
    # Render the template
    return await render_template(
        'dialogs.html',
        bot=bot,
        categories=categories,
        answers=answers,
        root_categories=root_categories,
    )

@dialogs_bp.route('/bot/<int:bot_id>/dialogs/add_answer', methods=['POST'])
@login_required
async def add_answer(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    answer_repo = current_app.repositories['answer_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))
    
    form = await request.form
    category_id = form.get('category_id')
    answer_text = form.get('answer_text')
    
    if not category_id or not answer_text:
        await flash('Необходимо указать категорию и текст ответа', 'error')
        return redirect(url_for('dialogs.dialogs', bot_id=bot_id))
    
    cleaned_text = await clean_html_content(answer_text)
    
    files = await request.files
    uploaded_file = files.get('answer_image')
    saved_path = None
    
    if uploaded_file and uploaded_file.filename:
        original_filename = secure_filename(uploaded_file.filename)
        unique_filename = await generate_unique_filename(original_filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            await uploaded_file.save(file_path)
            saved_path = file_path
        except Exception as e:
            await flash(f'Ошибка при загрузке файла: {str(e)}', 'error')
            return redirect(url_for('dialogs.dialogs', bot_id=bot_id))
    
    try:
        answer = await answer_repo.create_answer(
            category_id=int(category_id),
            text=cleaned_text,
            image_path=saved_path
        )
        await flash('Ответ успешно добавлен', 'success')
    except Exception as e:
        await flash(f'Ошибка при добавлении ответа: {str(e)}', 'error')
    
    return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

@dialogs_bp.route('/bot/<int:bot_id>/dialogs/add_category', methods=['POST'])
@login_required
async def add_category(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    category_repo = current_app.repositories['category_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))
    
    form = await request.form
    category_name = form.get('category_name')
    parent_id = form.get('parent_id')
    
    if category_name:
        try:
            await category_repo.create_category(
                name=category_name,
                bot_id=bot_id,
                parent_id=int(parent_id) if parent_id else None
            )
            await flash('Категория успешно добавлена', 'success')
        except Exception as e:
            await flash(f'Ошибка при создании категории: {str(e)}', 'error')
    else:
        await flash('Ошибка: Название категории не может быть пустым', 'error')
    
    return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

@dialogs_bp.route('/bot/<int:bot_id>/dialogs/delete_category', methods=['GET', 'POST'])
@login_required
async def delete_category(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    category_repo = current_app.repositories['category_repo']
    
    if request.method == 'GET':
        cat_id = int(request.args.get('cat_id'))
    else:  # POST
        form_data = await request.form
        cat_id = int(form_data.get('cat_id'))
    
    category = await category_repo.get_category_with_details(cat_id)
    if not category or category.bot_id != bot_id:
        await flash('Категория не найдена или у вас нет прав доступа', 'error')
        return redirect(url_for('dialogs.dialogs', bot_id=bot_id))
    
    if request.method == 'GET':
        return await render_template(
            'delete_category_confirm.html',
            category=category,
            bot_id=bot_id
        )
    elif request.method == 'POST':
        success = await category_repo.delete_category(cat_id)
        if success:
            await flash('Категория успешно удалена', 'success')
        else:
            await flash('Не удалось удалить категорию', 'error')
    
    return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

@dialogs_bp.route('/bot/<int:bot_id>/dialogs/delete_answer', methods=['POST'])
async def delete_answer(bot_id):
    logger.info(f"Entering delete_answer function for bot_id: {bot_id}")
    
    chatbot_repo = current_app.repositories['chatbot_repo']
    answer_repo = current_app.repositories['answer_repo']
    
    form = await request.form
    ans_id = form.get('ans_id')
    delete_image_only = form.get('delete_image_only') == 'true'
    
    if not ans_id:
        logger.warning("No answer ID provided")
        await flash('ID ответа не указан', 'error')
        return redirect(url_for('dialogs.dialogs', bot_id=bot_id))
    
    # Fetch the bot and validate access
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        logger.warning(f"Bot not found or access denied for bot_id: {bot_id}")
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))
    
    try:
        # Fetch the answer with its category eagerly loaded
        answer = await answer_repo.get_answer_with_category(int(ans_id))
        logger.debug(f"Retrieved answer: {answer}")
        
        if not answer or answer.category.bot_id != bot_id:
            logger.warning(f"Answer not found or doesn't belong to bot {bot_id}")
            await flash('Ответ не найден или у вас нет прав доступа', 'error')
            return redirect(url_for('dialogs.dialogs', bot_id=bot_id))
        
        if delete_image_only:
            if answer.image_path:
                try:
                    image_path = answer.image_path
                    await answer_repo.update_answer(answer.id, image_path=None)  # Remove image path from DB
                    logger.debug("Database updated, image path set to None")
                    
                    # Remove the file from the filesystem
                    if image_path and os.path.exists(image_path):
                        await asyncio.to_thread(os.remove, image_path)
                        logger.info(f"Image file removed: {image_path}")
                    else:
                        logger.warning(f"Image file not found: {image_path}")
                    
                    await flash('Изображение успешно удалено', 'success')
                except Exception as e:
                    logger.error(f"Error deleting image for answer {ans_id}: {str(e)}", exc_info=True)
                    await flash('Ошибка при удалении изображения', 'error')
            else:
                logger.info("No image to delete")
                await flash('У этого ответа нет изображения', 'warning')
        else:
            logger.info(f"Deleting entire answer {ans_id}")
            
            # Remove the associated image file if it exists
            if answer.image_path and os.path.exists(answer.image_path):
                try:
                    await asyncio.to_thread(os.remove, answer.image_path)
                    logger.info(f"Image file removed: {answer.image_path}")
                except Exception as e:
                    logger.error(f"Error removing image file: {str(e)}", exc_info=True)
            
            # Delete the answer from the database
            try:
                await answer_repo.delete_answer(answer.id)
                logger.info(f"Answer {ans_id} deleted from database")
                await flash('Ответ успешно удален', 'success')
            except Exception as e:
                logger.error(f"Error deleting answer from database: {str(e)}", exc_info=True)
                await flash('Ошибка при удалении ответа', 'error')
    except Exception as e:
        logger.error(f"Unexpected error in delete_answer: {str(e)}", exc_info=True)
        await flash('Произошла неожиданная ошибка', 'error')
    
    logger.info(f"Redirecting to dialogs page for bot {bot_id}")
    return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

@dialogs_bp.route('/bot/<int:bot_id>/dialogs/edit_answer', methods=['POST'])
@login_required
async def edit_answer(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    answer_repo = current_app.repositories['answer_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))
    
    form = await request.form
    ans_id = form.get('ans_id')
    new_text = form.get('new_text')
    
    cleaned_text = await clean_html_content(new_text)
    
    files = await request.files
    uploaded_file = files.get('new_image')
    saved_path = None
    
    if uploaded_file and uploaded_file.filename:
        original_filename = secure_filename(uploaded_file.filename)
        unique_filename = await generate_unique_filename(original_filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            await uploaded_file.save(file_path)
            saved_path = os.path.join('static/uploads', unique_filename)
            await flash('Новое изображение успешно загружено', 'success')
        except Exception as e:
            await flash(f'Ошибка при сохранении файла: {str(e)}', 'error')
            return redirect(url_for('dialogs.dialogs', bot_id=bot_id))
    
    if ans_id and cleaned_text:
        answer, answer_bot_id = await answer_repo.get_answer_with_bot_id(int(ans_id))
        if answer and answer_bot_id == bot_id:
            try:
                await answer_repo.update_answer(
                    answer_id=int(ans_id),
                    text=cleaned_text,
                    image_path=saved_path
                )
                await flash('Ответ успешно обновлен', 'success')
            except Exception as e:
                await flash(f'Ошибка при обновлении ответа: {str(e)}', 'error')
        else:
            await flash('Ошибка: Ответ не найден или не принадлежит данному боту', 'error')
    
    return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

@dialogs_bp.route('/bot/<int:bot_id>/dialogs/edit_category', methods=['POST'])
@login_required
async def edit_category(bot_id):
    chatbot_repo = current_app.repositories['chatbot_repo']
    category_repo = current_app.repositories['category_repo']
    
    bot = await chatbot_repo.get_bot_by_id(bot_id)
    if not bot or bot.user_id != int(current_user.auth_id):
        await flash('Бот не найден или у вас нет прав доступа', 'error')
        return redirect(url_for('bots.bots_list'))
    
    form = await request.form
    cat_id = form.get('cat_id')
    new_name = form.get('new_name')
    
    if cat_id and new_name:
        category = await category_repo.get_category_by_id(int(cat_id))
        if category and category.bot_id == bot_id:
            try:
                await category_repo.update_category(category_id=int(cat_id), name=new_name)
                await flash('Категория успешно обновлена', 'success')
            except Exception as e:
                await flash(f'Ошибка при обновлении категории: {str(e)}', 'error')
        else:
            await flash('Ошибка: Категория не найдена или не принадлежит данному боту', 'error')
    else:
        await flash('Ошибка: ID категории или новое имя не указаны', 'error')
    
    return redirect(url_for('dialogs.dialogs', bot_id=bot_id))









# from flask import Blueprint, request, render_template, redirect, url_for, flash, g, g
# from utils.html_utils import clean_html_content
# from utils.file_utils import generate_unique_filename
# from werkzeug.utils import secure_filename
# import os

# dialogs_bp = Blueprint('dialogs', __name__)

# @dialogs_bp.route('/bot/<int:bot_id>/dialogs')
# def dialogs(bot_id):
#     bot = g.chatbot_repo.get_bot_by_id(bot_id)
#     if not bot or bot.user_id != g.user.id:
#         flash('Бот не найден или у вас нет прав доступа', 'error')
#         return redirect(url_for('bots.bots_list'))
    
#     categories = g.category_repo.get_categories_by_bot_id(bot_id)
#     answers = g.answer_repo.get_answers_by_bot_id(bot_id)
#     root_categories = [c for c in categories if c.parent_id is None]

#     return render_template(
#         'dialogs.html',
#         bot=bot,
#         categories=categories,
#         answers=answers,
#         root_categories=root_categories,
#     )

# @dialogs_bp.route('/bot/<int:bot_id>/dialogs/add_answer', methods=['POST'])
# def add_answer(bot_id):
#     bot = g.chatbot_repo.get_bot_by_id(bot_id)
#     if not bot or bot.user_id != g.user.id:
#         flash('Бот не найден или у вас нет прав доступа', 'error')
#         return redirect(url_for('bots.bots_list'))

#     category_id = request.form.get('category_id')
#     answer_text = request.form.get('answer_text')
#     cleaned_text = clean_html_content(answer_text)

#     uploaded_file = request.files.get('answer_image')
#     saved_path = None

#     if uploaded_file and uploaded_file.filename:
#         original_filename = secure_filename(uploaded_file.filename)
#         unique_filename = generate_unique_filename(original_filename)
#         file_path = os.path.join(g.config['UPLOAD_FOLDER'], unique_filename)
#         try:
#             uploaded_file.save(file_path)
#             saved_path = os.path.join('uploads', unique_filename)
#             flash('Изображение успешно загружено', 'success')
#         except Exception as e:
#             flash(f"Ошибка при сохранении файла: {str(e)}", "error")
#             return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

#     if category_id and cleaned_text:
#         g.answer_repo.create_answer(
#             category_id=int(category_id),
#             text=cleaned_text,
#             image_path=saved_path
#         )
#         flash('Ответ успешно добавлен', 'success')

#     return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

# @dialogs_bp.route('/bot/<int:bot_id>/dialogs/add_category', methods=['POST'])
# def add_category(bot_id):
#     bot = g.chatbot_repo.get_bot_by_id(bot_id)
#     if not bot or bot.user_id != g.user.id:
#         flash('Бот не найден или у вас нет прав доступа', 'error')
#         return redirect(url_for('bots.bots_list'))

#     category_name = request.form.get('category_name')
#     parent_id = request.form.get('parent_id')
#     if category_name:
#         g.category_repo.create_category(
#             name=category_name,
#             bot_id=bot_id,
#             parent_id=int(parent_id) if parent_id else None
#         )
#         flash('Категория успешно добавлена', 'success')
#     else:
#         flash('Ошибка: Название категории не может быть пустым', 'error')
#     return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

# @dialogs_bp.route('/bot/<int:bot_id>/dialogs/delete_category', methods=['POST'])
# def delete_category(bot_id):
#     bot = g.chatbot_repo.get_bot_by_id(bot_id)
#     if not bot or bot.user_id != g.user.id:
#         flash('Бот не найден или у вас нет прав доступа', 'error')
#         return redirect(url_for('bots.bots_list'))

#     cat_id = request.form.get('cat_id')
#     if cat_id:
#         category = g.category_repo.get_category_by_id(cat_id)
#         if category and category.bot_id == bot_id:
#             g.category_repo.delete_category(cat_id)
#             flash(f'Категория "{category.name}" успешно удалена', 'success')
#         else:
#             flash('Ошибка: Категория не найдена или не принадлежит данному боту', 'error')
#     else:
#         flash('Ошибка: ID категории не указан', 'error')

#     return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

# @dialogs_bp.route('/bot/<int:bot_id>/dialogs/delete_answer', methods=['POST'])
# def delete_answer(bot_id):
#     bot = g.chatbot_repo.get_bot_by_id(bot_id)
#     if not bot or bot.user_id != g.user.id:
#         flash('Бот не найден или у вас нет прав доступа', 'error')
#         return redirect(url_for('bots.bots_list'))

#     ans_id = request.form.get('ans_id')
#     delete_image_only = request.form.get('delete_image_only') == 'true'

#     if ans_id:
#         answer = g.answer_repo.get_answer_by_id(int(ans_id))
#         if answer and answer.category.bot_id == bot_id:
#             if delete_image_only:
#                 if answer.image_path:
#                     # Удаляем только изображение
#                     g.answer_repo.update_answer(answer.id, image_path=None)
#                     flash('Изображение успешно удалено', 'success')
#                 else:
#                     flash('У этого ответа нет изображения', 'warning')
#             else:
#                 # Удаляем весь ответ
#                 g.answer_repo.delete_answer(int(ans_id))
#                 flash('Ответ успешно удален', 'success')
#         else:
#             flash('Ошибка: Ответ не найден или не принадлежит данному боту', 'error')
#     return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

# @dialogs_bp.route('/bot/<int:bot_id>/dialogs/edit_answer', methods=['POST'])
# def edit_answer(bot_id):
#     bot = g.chatbot_repo.get_bot_by_id(bot_id)
#     if not bot or bot.user_id != g.user.id:
#         flash('Бот не найден или у вас нет прав доступа', 'error')
#         return redirect(url_for('bots.bots_list'))

#     ans_id = request.form.get('ans_id')
#     new_text = request.form.get('new_text')
#     cleaned_text = clean_html_content(new_text)

#     uploaded_file = request.files.get('new_image')
#     saved_path = None

#     if uploaded_file and uploaded_file.filename:
#         original_filename = secure_filename(uploaded_file.filename)
#         unique_filename = generate_unique_filename(original_filename)
#         file_path = os.path.join(g.config['UPLOAD_FOLDER'], unique_filename)
#         try:
#             uploaded_file.save(file_path)
#             saved_path = os.path.join('static/uploads', unique_filename)
#             flash('Новое изображение успешно загружено', 'success')
#         except Exception as e:
#             flash(f'Ошибка при сохранении файла: {str(e)}', 'error')
#             return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

#     if ans_id and cleaned_text:
#         answer, answer_bot_id = g.answer_repo.get_answer_with_bot_id(int(ans_id))
#         if answer and answer_bot_id == bot_id:
#             g.answer_repo.update_answer(
#                 answer_id=int(ans_id),
#                 text=cleaned_text,
#                 image_path=saved_path
#             )
#             flash('Ответ успешно обновлен', 'success')
#         else:
#             flash('Ошибка: Ответ не найден или не принадлежит данному боту', 'error')

#     return redirect(url_for('dialogs.dialogs', bot_id=bot_id))

# @dialogs_bp.route('/bot/<int:bot_id>/dialogs/edit_category', methods=['POST'])
# def edit_category(bot_id):
#     bot = g.chatbot_repo.get_bot_by_id(bot_id)
#     if not bot or bot.user_id != g.user.id:
#         flash('Бот не найден или у вас нет прав доступа', 'error')
#         return redirect(url_for('bots.bots_list'))

#     cat_id = request.form.get('cat_id')
#     new_name = request.form.get('new_name')
#     if cat_id and new_name:
#         category = g.category_repo.get_category_by_id(int(cat_id))
#         if category and category.bot_id == bot_id:
#             g.category_repo.update_category(category_id=int(cat_id), name=new_name)
#             flash('Категория успешно обновлена', 'success')
#         else:
#             flash('Ошибка: Категория не найдена или не принадлежит данному боту', 'error')
#     else:
#         flash('Ошибка: ID категории или новое имя не указаны', 'error')
#     return redirect(url_for('dialogs.dialogs', bot_id=bot_id))