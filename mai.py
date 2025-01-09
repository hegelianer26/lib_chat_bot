from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor
from multiprocessing import Process
from vkbottle_types.events import GroupEventType, GroupTypes


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database3.db'
db = SQLAlchemy(app)

token = 'vk1.a.W0vw0HM-535XGcE6fIFASzkf83ZILxvzbZS9nlHAsv8ZOFsbVAPoaxcvcbKOUNJaKktyoqSC7NmPDaaMpd5-tkv95XOyqZOCn9LN-vUrAN_6QP6hgIhSjOhkW3fjOfxPMQYqaMvhsyzU8ieaumF3iFO1a20omqpmtQpHV3FaB8sXochhWasGISdNc5lJVTaXF2kANrzrZKxi4C_hn81sGw'

app_context = app.app_context()
app_context.push()

bot = Bot(token=token)

# Модель категории (позволяет многоуровневую вложенность)
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)

    parent = db.relationship('Category', remote_side=[id], backref='children', lazy='joined')

# Модель для ответов (привязка к категории)
class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

    category = db.relationship('Category', backref='answers', lazy=True)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')

        # Добавление категории, включая вложенную (выбираем parent_id)
        if action == 'add_category':
            parent_id = request.form.get('parent_id')
            cat_name = request.form.get('category_name')
            if cat_name:
                if parent_id:
                    new_cat = Category(name=cat_name, parent_id=int(parent_id))
                else:
                    new_cat = Category(name=cat_name)
                db.session.add(new_cat)
                db.session.commit()

        # Добавление ответа
        elif action == 'add_answer':
            category_id = request.form.get('category_id')
            answer_text = request.form.get('answer_text')
            if category_id and answer_text:
                ans = Answer(category_id=int(category_id), text=answer_text)
                db.session.add(ans)
                db.session.commit()

        # Удаляем категорию и все её дочерние
        elif action == 'delete_category':
            cat_id = request.form.get('cat_id')
            if cat_id:
                cat_obj = Category.query.get(cat_id)
                if cat_obj:
                    # Удаляем все ответы категории
                    for ans in cat_obj.answers:
                        db.session.delete(ans)
                    # Удаляем все вложенные категории
                    def delete_subcats(c):
                        for subc in c.children:
                            for subans in subc.answers:
                                db.session.delete(subans)
                            delete_subcats(subc)
                            db.session.delete(subc)
                    delete_subcats(cat_obj)
                    db.session.delete(cat_obj)
                    db.session.commit()

        # Удаляем отдельный ответ
        elif action == 'delete_answer':
            ans_id = request.form.get('ans_id')
            if ans_id:
                ans_obj = Answer.query.get(ans_id)
                if ans_obj:
                    db.session.delete(ans_obj)
                    db.session.commit()

        return redirect(url_for('admin'))

    categories = Category.query.all()
    answers = Answer.query.all()
    return render_template('admin.html', categories=categories, answers=answers)

@app.route('/')
def index():
    return "Главная страница"

def build_categories_keyboard(parent_id=None, current_path=None):
    try:
        keyboard = Keyboard(one_time=False, inline=False)
        categories = Category.query.filter_by(parent_id=parent_id).all()

        if not categories and not parent_id:
            keyboard.add(Text(
                label="Нет доступных категорий",
                payload={"cmd": "main_menu"}
            ), color=KeyboardButtonColor.SECONDARY)
            return keyboard.get_json()

        for cat in categories:
            keyboard.add(Text(
                label=cat.name,
                payload={
                    "cmd": "show_category",
                    "cat_id": cat.id,
                    "parent_id": parent_id if parent_id else 0,
                    "path": current_path + [cat.name] if current_path else [cat.name]
                }
            ), color=KeyboardButtonColor.PRIMARY)
            keyboard.row()

        if parent_id:
            parent_category = Category.query.get(parent_id)
            if parent_category and parent_category.parent_id:
                keyboard.add(Text(
                    label="⬅ Назад",
                    payload={
                        "cmd": "go_back",
                        "parent_id": parent_category.parent_id,
                        "path": current_path[:-1] if current_path else None
                    }
                ), color=KeyboardButtonColor.SECONDARY)
            else:
                keyboard.add(Text(
                    label="⬅ В главное меню",
                    payload={"cmd": "main_menu"}
                ), color=KeyboardButtonColor.SECONDARY)

        return keyboard.get_json()
    except Exception as e:
        print(f"[LOG] Ошибка при создании клавиатуры: {e}")
        keyboard = Keyboard(one_time=False, inline=False)
        keyboard.add(Text(
            label="⚠ Ошибка! В главное меню",
            payload={"cmd": "main_menu"}
        ), color=KeyboardButtonColor.NEGATIVE)
        return keyboard.get_json()

@bot.on.raw_event(GroupEventType.MESSAGE_NEW)
async def debug_event(event: GroupTypes.MessageNew):
    print("[LOG] RAW EVENT:", event)

@bot.on.message(payload={"cmd": "main_menu"})
async def main_menu_handler(message: Message):
    print(f"[LOG] main_menu_handler triggered with message text: {message.text}, payload: {message.payload}")
    keyboard = build_categories_keyboard(None)
    await message.answer("Главное меню:", keyboard=keyboard)
    print("[LOG] main_menu_handler completed")

@bot.on.message(payload={"cmd": "show_category"})
async def show_category_handler(message: Message):
    print(f"[LOG] show_category_handler triggered with payload: {message.payload}")
    try:
        cat_id = message.payload["cat_id"]
        current_path = message.payload.get("path", [])
        cat = Category.query.get(cat_id)

        if not cat:
            print(f"[LOG] Категория не найдена, cat_id: {cat_id}")
            keyboard = build_categories_keyboard(None)
            await message.answer("Категория не найдена", keyboard=keyboard)
            return

        answers = Answer.query.filter_by(category_id=cat_id).all()
        
        if answers:
            answer_text = "\n\n".join([answer.text for answer in answers])
            keyboard = build_categories_keyboard(cat.parent_id, current_path[:-1])
            print(f"[LOG] Sending answers for cat_id {cat_id}")
            await message.answer(answer_text, keyboard=keyboard)
            return

        if cat.children:
            keyboard = build_categories_keyboard(cat.id, current_path)
            await message.answer(
                f"Категория: {' > '.join(current_path)}\nВыберите подкатегорию:", 
                keyboard=keyboard
            )
        else:
            keyboard = build_categories_keyboard(cat.parent_id, current_path[:-1])
            await message.answer("В данной категории нет информации", keyboard=keyboard)
    except Exception as e:
        print(f"[LOG] Ошибка в show_category_handler: {e}")
        keyboard = build_categories_keyboard(None)
        await message.answer("Произошла ошибка", keyboard=keyboard)
    finally:
        print("[LOG] show_category_handler completed")

@bot.on.message(payload={"cmd": "go_back"})
async def go_back_handler(message: Message):
    print(f"[LOG] go_back_handler triggered with payload: {message.payload}")
    try:
        current_parent_id = message.payload.get("parent_id")
        current_path = message.payload.get("path", [])
        
        if not current_parent_id:
            keyboard = build_categories_keyboard(None)
            await message.answer("Главное меню:", keyboard=keyboard)
            return

        current_cat = Category.query.get(current_parent_id)
        if not current_cat:
            keyboard = build_categories_keyboard(None)
            await message.answer("Категория не найдена", keyboard=keyboard)
            return

        keyboard = build_categories_keyboard(current_cat.parent_id, current_path)
        await message.answer(
            f"Категория: {' > '.join(current_path) if current_path else 'Главное меню'}", 
            keyboard=keyboard
        )
    except Exception as e:
        print(f"[LOG] Ошибка в go_back_handler: {e}")
        keyboard = build_categories_keyboard(None)
        await message.answer("Произошла ошибка", keyboard=keyboard)
    finally:
        print("[LOG] go_back_handler completed")

@bot.on.message(text=["меню", "Меню"])
async def text_menu_handler(message: Message):
    print(f"[LOG] text_menu_handler triggered with message text: {message.text}")
    keyboard = build_categories_keyboard(None)
    await message.answer("Главное меню:", keyboard=keyboard)
    print("[LOG] text_menu_handler completed")

@bot.on.message()
async def default_handler(message: Message):
    print(f"[LOG] default_handler triggered with message text: {message.text}, payload: {message.payload}")
    if message.text:
        category = Category.query.filter_by(name=message.text).first()
        if category:
            keyboard = build_categories_keyboard(category.id, [category.name])
            print(f"[LOG] Found category: {category.name} (id: {category.id})")
            await message.answer(
                f"Категория: {category.name}",
                keyboard=keyboard
            )
            answers = Answer.query.filter_by(category_id=category.id).all()
            if answers:
                answer_text = "\n\n".join([answer.text for answer in answers])
                print(f"[LOG] Sending answers for category: {category.name}")
                await message.answer(answer_text)
            elif category.children:
                print(f"[LOG] Category has subcategories: {category.name}")
                await message.answer("Выберите подкатегорию:")
            return
    keyboard = build_categories_keyboard(None)
    await message.answer("Выберите категорию:", keyboard=keyboard)
    print("[LOG] default_handler completed")

if __name__ == '__main__':
    # def run_flask():
    #     app.run(port=5001, debug=True)

    # flask_process = Process(target=run_flask)
    # flask_process.start()
    bot.run_forever()
    # try:
    #     bot.run_forever()
    # except KeyboardInterrupt:
    #     print("[LOG] Завершение работы бота...")
    # finally:
    #     flask_process.terminate()
    #     flask_process.join()