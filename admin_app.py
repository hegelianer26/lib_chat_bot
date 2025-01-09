from flask import Flask, request, render_template, redirect, url_for, jsonify
from db.database import init_db 
import db.service_standalone as db_service
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json
from flask import flash
from dotenv import load_dotenv, set_key
from bs4 import BeautifulSoup

load_dotenv() 

app = Flask("chatbot_admin", template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Папка для сохранения загруженных файлов
app.secret_key = os.getenv('FLASK_SECRET_KEY')

CONFIG_FILE = 'config.json'


def clean_html_content(html_content):
    """Remove HTML tags but preserve emojis and basic formatting like newlines and paragraphs"""
    if not html_content:
        return ""

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Replace <br>, <p>, and <div> with newlines
    for tag in soup.find_all(['br', 'p', 'div']):
        tag.insert_before('\n')
        tag.insert_after('\n')

    # Get text and retain all newlines
    text = soup.get_text(separator='\n')

    return text.strip()

@app.route('/')
def index():
    return render_template(
        'index.html',
    )

@app.route('/dialogs', methods=['GET', 'POST'])
def dialogs():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_answer':
            category_id = request.form.get('category_id')
            answer_text = request.form.get('answer_text')
            
            # Clean HTML from TinyMCE
            cleaned_text = clean_html_content(answer_text)
            
            uploaded_file = request.files.get('answer_image')
            saved_path = None

            if uploaded_file and uploaded_file.filename:
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)
                saved_path = os.path.join('uploads', filename)

            if category_id and cleaned_text:
                db_service.create_answer(
                    category_id=int(category_id),
                    text=cleaned_text,
                    image_path=saved_path
                )

        elif action == 'add_category':
            category_name = request.form.get('category_name')
            parent_id = request.form.get('parent_id')
            if category_name:
                db_service.create_category(
                    name=category_name,
                    parent_id=int(parent_id) if parent_id else None
                )
                flash('Категория успешно добавлена', 'success')
            else:
                flash('Ошибка: Название категории не может быть пустым', 'error')

        elif action == 'delete_category':
            cat_id = request.form.get('cat_id')
            if cat_id:
                db_service.delete_category(int(cat_id))

        elif action == 'delete_answer':
            ans_id = request.form.get('ans_id')
            if ans_id:
                db_service.delete_answer(int(ans_id))

        elif action == 'delete_image':
            ans_id = request.form.get('ans_id')
            if ans_id:
                remove_answer_image(int(ans_id))

        elif action == 'edit_category':
            cat_id = request.form.get('cat_id')
            new_name = request.form.get('new_name')
            if cat_id and new_name:
                db_service.update_category_name(int(cat_id), new_name)

        elif action == 'edit_answer':
            ans_id = request.form.get('ans_id')
            new_text = request.form.get('new_text')
            
            # Clean HTML from TinyMCE
            cleaned_text = clean_html_content(new_text)
            
            uploaded_file = request.files.get('new_image')
            saved_path = None

            if uploaded_file and uploaded_file.filename:
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)
                saved_path = os.path.join('uploads', filename)

            if ans_id and cleaned_text:
                db_service.update_answer(
                    answer_id=int(ans_id),
                    new_text=cleaned_text,
                    new_image_path=saved_path
                )

        return redirect(url_for('dialogs'))

    categories = db_service.get_all_categories()
    answers = db_service.get_all_answers()
    root_categories = [c for c in categories if c.parent_id is None]

    return render_template(
        'dialogs.html',
        categories=categories,
        answers=answers,
        root_categories=root_categories,
    )



@app.route('/statistics')
def statistics():
    return render_template(
        'statistics.html'
    )

@app.route('/api/statistics/overview')
def get_statistics_overview():
    # Get date range from query params
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get statistics data
    user_activity = db_service.get_user_activity(start_date, end_date)
        
    return jsonify({
        'user_activity': [
            {'user_id': user_id, 'actions': count}
            for user_id, count in user_activity
        ],
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
    })


@app.route('/api/statistics/daily')
def get_daily_statistics():
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    daily_stats = db_service.get_daily_statistics(start_date, end_date)
    
    return jsonify({
        'daily_activity': [
            {
                'date': date,
                'count': count,
                'users_count': users_count
            }
            for date, count, users_count in daily_stats
        ]
    })


@app.route('/api/statistics/queries')
def get_query_statistics():
    limit = request.args.get('limit', 10, type=int)
    queries = db_service.get_query_statistics(limit)
    
    return jsonify({
        'popular_queries': [
            {'query': text, 'count': count}
            for text, count in queries
        ]
    })



@app.route('/api/statistics/users')
def get_user_statistics():
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    stats = db_service.get_user_activity_statistics(start_date, end_date)
    
    return jsonify({
        'user_stats': [
            {'user_id': user_id, 'count': count}
            for user_id, count in stats
        ]
    })

@app.route('/api/statistics/failed-queries')
def get_failed_queries_statistics():
    failed_queries = db_service.get_failed_queries()
    
    return jsonify({
        'queries': [
            {'query': text, 'count': count}
            for text, count in failed_queries
        ]
    })


# admin_app.py
@app.route('/users')
def users_list():
    users_stats = db_service.get_users_detailed_statistics()
    return render_template('users.html', users=users_stats)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'vk_token': '', 'database_url': 'sqlite:///bot.db'}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        vk_token = request.form.get('vk_token')
        database_url = request.form.get('database_url')
        
        # Обновляем только если значения были предоставлены
        if vk_token:
            set_key('.env', 'VK_TOKEN', vk_token)
        if database_url:
            set_key('.env', 'DATABASE_URL', database_url)
            try:
                init_db(database_url)
                flash('Конфигурация успешно сохранена', 'success')
            except Exception as e:
                flash(f'Ошибка при подключении к БД: {str(e)}', 'error')
        
        return redirect(url_for('config'))

    # Получаем текущие значения из .env
    current_config = {
        'vk_token': os.getenv('VK_TOKEN', ''),
        'database_url': os.getenv('DATABASE_URL', 'sqlite:///bot.db')
    }
    
    return render_template('config.html', config=current_config)


def remove_answer_image(answer_id):
    """
    Remove an answer's image from the filesystem and update the answer's image path to None.

    Args:
        answer_id (int): The ID of the answer to remove the image from.
    """
    answer = db_service.get_answer_by_id(answer_id)
    if answer and answer.image_path:
        # Remove the image file from the filesystem
        image_path = os.path.join('static', answer.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
        
        # Update the answer image path to None
        db_service.update_answer_image_path(answer_id, None)










if __name__ == '__main__':
    # Перед запуском Flask-приложения вызываем инициализацию таблиц
    init_db()
    app.run(debug=True, port=5001)