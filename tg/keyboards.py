from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# Ипортируем билдер, который может подставлять значения в клавиатуру, переданные из вне, или предопределенные
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# создаем кнопки клавитуры с помошью реплай кейборд
# resize_keyboard=True Меняем размер клавиатуры до минимального значения
# input_field_placeholder вместо  подсказки значения(write a message)
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Первокурсникам"), KeyboardButton(text="Режим работы")],
        [KeyboardButton(text="Получить читательский")],
        [KeyboardButton(text="Активности"), KeyboardButton(text="Услуги")],
        [KeyboardButton(text="Языковые клубы"), KeyboardButton(text="Печатные книги")],
        [KeyboardButton(text="Электронные ресурсы")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню",
)
# Клавиатура первокурсникам
firstcourse = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="График выдачи учебной литературы")],
        [KeyboardButton(text="О библиотеке")],
        [KeyboardButton(text='Мобильное приложение "Научка"')],
        [KeyboardButton(text="Книжная полка первокурсника")],
        [KeyboardButton(text="Получить читательский")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите что интересует",
)
# Клавиатура получить читательский
get_reader_card = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Студент или сотрудник ТГУ")],
        [KeyboardButton(text="Студент или сотрудник ВУЗов Томска")],
        [KeyboardButton(text="Сторонний пользователь")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите роль",
)
# Клавиатура активности
activnosti = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="VR выставки"), KeyboardButton(text="Экскурсии")],
        [KeyboardButton(text="Квесты"), KeyboardButton(text="Стать волонтером")],
        [KeyboardButton(text="Факты о научке"), KeyboardButton(text="Настолки")],
        [KeyboardButton(text="Языковые клубы"), KeyboardButton(text="Подкасты")],
        [KeyboardButton(text="Фотосессия в библиотеке")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите активность",
)

kvesty = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='"В плену книжных стеллажей"')],
        [KeyboardButton(text='"Загадки города Томска"')],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите квест",
)

podkast = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Как это было")],
        [KeyboardButton(text="Библиомаршрут")],
        [KeyboardButton(text="Фронтиспис: Кабинет Пушкинского")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите подкаст",
)

language_clubs = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Английский"),
            KeyboardButton(text="Арабский"),
            KeyboardButton(text="Немецкий"),
        ],
        [
            KeyboardButton(text="Русский"),
            KeyboardButton(text="Испанский"),
            KeyboardButton(text="Китайский"),
        ],
        [KeyboardButton(text="Французский"), KeyboardButton(text="Итальянский")],
        [KeyboardButton(text="Индонезийский"), KeyboardButton(text="Монгольский")],
        [
            KeyboardButton(text="Бенгальский"),
            KeyboardButton(text="ComPass"),
            KeyboardButton(text="Speak Dating"),
        ],
        [
            KeyboardButton(text="Games Club"),
            KeyboardButton(text="Урду"),
        ],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите Языковой клуб",
)

el_resourses = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Электронный каталог")],
        [KeyboardButton(text="Электронная библиотека")],
        [KeyboardButton(text="PRO Сибирь")],
        [KeyboardButton(text="Удаленный доступ")],
        [KeyboardButton(text="Базы данных")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите электронный ресурс'",
)

# Клавиатура Услуг
servises = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Бронирование аудиторий")],
        [KeyboardButton(text="Оформление работ"), KeyboardButton(text="Антиплагиат")],
        [KeyboardButton(text="Ксерокопия, распечатка")],
        [KeyboardButton(text="Заказать книгу, статью из НБ")],
        [KeyboardButton(text="Заказать литературу из других библиотек")],
        [KeyboardButton(text="Ноутбуки напрокат"), KeyboardButton(text="УДК и ББК")],
        [KeyboardButton(text="Фотосессия в библиотеке")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите услугу",
)

# Клавиатура Бронирование аудиторий
booking = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Забронировать")],
        [KeyboardButton(text="Помещения и оборудование")],
        [KeyboardButton(text="Сторонним посетителям")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт",
)

# Клавиатура забронировать
booking_now = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="AppStore",
                url="https://clck.ru/XWuPS",
            )
        ],
        [
            InlineKeyboardButton(
                text="GooglePlay ",
                url="https://play.google.com/store/apps/details?id=com.tsu.bible",
            )
        ],
        [
            InlineKeyboardButton(
                text="Бронь конференц-залов",
                url="https://it.tsu.ru/index.php/konferents-zaly-rezervirovanie",
            )
        ],
        [
            InlineKeyboardButton(
                text="Бронь помещений",
                url="https://www.lib.tsu.ru/ru/meropriyatiya-v-nauchnoy-biblioteke",
            )
        ],
    ]
)


form_order = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Оформить список литературы",
                url="http://service.lib.tsu.ru/digital-services-start",
            )
        ],
    ]
)


form_work = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Гост"), KeyboardButton(text="Консультация")],
        [KeyboardButton(text="Заказать оформление")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт",
)


printed_books = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Найти книгу"), KeyboardButton(text="Заказать книгу")],
        [KeyboardButton(text="Брать книги на дом")],
        [KeyboardButton(text="Продлить книги"), KeyboardButton(text="Сдать книги")],
        [KeyboardButton(text="Отслеживать задолженность")],
        [KeyboardButton(text="Подарить книгу библиотеке")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт",
)

rent_book_for_home = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Студент или сотрудник ТГУ.")],
        [KeyboardButton(text="Студент или сотрудник ВУЗов Томска.")],
        [KeyboardButton(text="Сторонний пользователь.")],
        [KeyboardButton(text="Меню")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт",
)

# клавиатура для инлайнов
""" main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Первокурсникам", callback_data="firstcourse")],
        [
            InlineKeyboardButton(text="Режим работы", callback_data="worktime"),
            InlineKeyboardButton(
                text="Получить читательский", callback_data="get_reader_cart"
            ),
        ],
    ]
) """

settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Зарегистрироваться",
                url="https://forms.yandex.ru/u/64337fae02848f1e65e96c3c/",
            )
        ]
    ]
)

# значения билдера
roles = ["Сотрудник ТГУ", "Студент ТГУ", "Сторонний пользователь"]


async def Reply_roles():
    keyboard = ReplyKeyboardBuilder()
    for role in roles:
        keyboard.add(KeyboardButton(text=role))
    return keyboard.adjust(2).as_markup()


async def Inline_roles():
    keyboard = InlineKeyboardBuilder()
    for role in roles:
        keyboard.add(InlineKeyboardButton(text=role, callback_data=f"role_{role}"))
    return keyboard.adjust(2).as_markup()


# as_markup use always
