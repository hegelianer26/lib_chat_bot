from quart import Blueprint, request, render_template, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from quart_auth import login_user, logout_user, login_required, current_user, AuthUser
from db.models import User
import logging

users_bp = Blueprint('users', __name__)

logger = logging.getLogger(__name__)

@users_bp.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
async def user_detail(user_id):
    # Используем current_app.repositories вместо g.db
    user_repo = current_app.repositories['user_repo']
    
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        await flash('Пользователь не найден', 'error')
        return redirect(url_for('users.users_list'))
    
    if request.method == 'POST':
        form_data = await request.form
        update_data = {
            'first_name': form_data.get('first_name'),
            'last_name': form_data.get('last_name'),
            'email': form_data.get('email'),
            'organization_name': form_data.get('organization_name')
        }
        
        new_password = form_data.get('new_password')
        if new_password:
            confirm_password = form_data.get('confirm_password')
            if new_password != confirm_password:
                await flash('Пароли не совпадают', 'error')
                return await render_template('user_detail.html', user=user)
            else:
                user.set_password(new_password)
        
        updated_user = await user_repo.update_user(user.id, **update_data)
        
        if updated_user:
            await flash('Профиль успешно обновлен', 'success')
        else:
            await flash('Не удалось обновить профиль', 'error')
        
        return redirect(url_for('users.user_detail', user_id=user.id))
    
    return await render_template('user_detail.html', user=user)

@users_bp.route('/register', methods=['GET', 'POST'])
async def register():
    user_repo = current_app.repositories['user_repo']
    
    if request.method == 'POST':
        form_data = await request.form
        email = form_data['email']
        password = form_data['password']
        confirm_password = form_data['confirm_password']
        
        if password != confirm_password:
            await flash('Пароли не совпадают', 'error')
            return await render_template('register.html')
        
        existing_user = await user_repo.get_user_by_email(email)
        if existing_user:
            await flash('Пользователь с таким email уже существует', 'error')
            return await render_template('register.html')
        
        user = User(email=email)
        user.set_password(password)
        await user_repo.create_user(user)
        await flash('Регистрация успешна', 'success')
        return redirect(url_for('users.login'))
    
    return await render_template('register.html')

@users_bp.route('/login', methods=['GET', 'POST'])
async def login():
    if await current_user.is_authenticated:
        logger.info("User is already authenticated.")
        return redirect(url_for('bots.bots_list'))

    if request.method == 'POST':
        form_data = await request.form
        email = form_data['email']
        password = form_data['password']

        logger.debug(f"Login attempt for email: {email}")

        user_repo = current_app.repositories['user_repo']
        user = await user_repo.get_user_by_email(email)

        if user:
            logger.debug(f"User found: {user.id}")
        else:
            logger.warning(f"User not found for email: {email}")

        if user and user.check_password(password):
            auth_user = AuthUser(auth_id=str(user.id))
            login_user(auth_user)
            logger.info(f"User {auth_user.auth_id} logged in successfully.")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('bots.bots_list'))
        else:
            logger.warning(f"Failed login attempt for email: {email}")
            await flash('Неверный email или пароль', 'error')

    return await render_template('login.html')

@users_bp.route('/logout')
@login_required
async def logout():
    logout_user()
    await flash('Вы вышли из системы', 'success')
    return redirect(url_for('users.login'))


# from flask import Blueprint, request, render_template, redirect, url_for, flash, g
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import login_user, login_required, logout_user, current_user
# from db.models import User


# users_bp = Blueprint('users', __name__)

# @users_bp.route('/users')
# def users_list():
#     users = g.user_repo.get_all_users()
#     return render_template('users.html', users=users)

# @users_bp.route('/user/<int:user_id>', methods=['GET', 'POST'])
# @login_required
# def user_detail(user_id):
#     user = g.user_repo.get_user_by_id(user_id)
#     if not user:
#         flash('Пользователь не найден', 'error')
#         return redirect(url_for('users.users_list'))
    
#     if request.method == 'POST':
#         # Создаем словарь с обновленными данными
#         update_data = {
#             'first_name': request.form.get('first_name'),
#             'last_name': request.form.get('last_name'),
#             'email': request.form.get('email'),
#             'organization_name': request.form.get('organization_name')
#         }
        
#         new_password = request.form.get('new_password')
#         if new_password:
#             if new_password == request.form.get('confirm_password'):
#                 user.set_password(new_password)
#             else:
#                 flash('Пароли не совпадают', 'error')
#                 return render_template('user_detail.html', user=user)
        
#         # Обновляем пользователя
#         updated_user = g.user_repo.update_user(user.id, **update_data)
        
#         if updated_user:
#             flash('Профиль успешно обновлен', 'success')
#         else:
#             flash('Не удалось обновить профиль', 'error')
        
#         return redirect(url_for('users.user_detail', user_id=user.id))
    
#     return render_template('user_detail.html', user=user)


# @users_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         confirm_password = request.form['confirm_password']
        
#         if password != confirm_password:
#             flash('Пароли не совпадают', 'error')
#         elif g.user_repo.get_user_by_email(email):
#             flash('Пользователь с таким email уже существует', 'error')
#         else:
#             user = User(email=email)
#             user.set_password(password)
#             g.user_repo.create_user(user)
#             flash('Регистрация успешна', 'success')
#             return redirect(url_for('users.login'))
#     return render_template('register.html')


# @users_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('bots.bots_list'))
    
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         user = g.user_repo.get_user_by_email(email)
        
#         if user and user.check_password(password):
#             login_user(user)
#             flash('Вход выполнен успешно', 'success')
#             next_page = request.args.get('next')
#             return redirect(next_page or url_for('bots.bots_list'))
#         else:
#             flash('Неверный email или пароль', 'error')
#     return render_template('login.html')


# @users_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('Вы вышли из системы', 'success')
#     return redirect(url_for('users.login'))