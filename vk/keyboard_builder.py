from vkbottle import Keyboard, Text, KeyboardButtonColor

class KeyboardBuilder:
    def __init__(self, vk_handler):
        self.vk_handler = vk_handler

    async def build_categories_keyboard(self, parent_id=None, current_path=None):
        try:
            keyboard = Keyboard(one_time=False, inline=False)
            categories = await self.vk_handler.get_categories(parent_id)

            if not parent_id:
                # Добавляем кнопку "Поиск в каталоге" только в главном меню
                keyboard.add(
                    Text("🔍 Поиск в каталоге", payload={"cmd": "catalog_search"}),
                    color=KeyboardButtonColor.PRIMARY
                )
                keyboard.row()

            # Отображаем только корневые категории, если parent_id не указан
            if parent_id is None:
                categories = [cat for cat in categories if cat.get('parent_id') is None]

            short_cats = []
            long_cats = []

            # Разделяем категории на короткие и длинные названия
            for category in categories:
                if len(category['name']) <= 16:
                    short_cats.append(category)
                else:
                    long_cats.append(category)

            # Две колонки для коротких названий
            for i in range(0, len(short_cats), 2):
                row_cats = short_cats[i:i + 2]
                for cat in row_cats:
                    keyboard.add(
                        Text(
                            label=cat['name'],
                            payload={
                                "cmd": "show_category",
                                "cat_id": cat['id'],
                                "parent_id": parent_id if parent_id else 0,
                                "path": (current_path + [cat['name']]) if current_path else [cat['name']]
                            }
                        ),
                        color=KeyboardButtonColor.SECONDARY
                    )
                keyboard.row()

            # Одна колонка для длинных названий
            for cat in long_cats:
                keyboard.add(
                    Text(
                        label=cat['name'],
                        payload={
                            "cmd": "show_category",
                            "cat_id": cat['id'],
                            "parent_id": parent_id if parent_id else 0,
                            "path": (current_path + [cat['name']]) if current_path else [cat['name']]
                        }
                    ),
                    color=KeyboardButtonColor.SECONDARY
                )
                keyboard.row()

            # Добавляем кнопку "Назад" или "В главное меню"
            if parent_id:
                parent_category = await self.vk_handler.get_category_by_id(parent_id)
                if parent_category and parent_category.get('parent_id'):
                    keyboard.add(
                        Text(
                            label="⬅ Назад",
                            payload={
                                "cmd": "go_back",
                                "parent_id": parent_category['parent_id'],
                                "path": current_path[:-1] if current_path else None
                            }
                        ),
                        color=KeyboardButtonColor.PRIMARY
                    )
                else:
                    keyboard.add(
                        Text("⬅ В главное меню", payload={"cmd": "main_menu"}),
                        color=KeyboardButtonColor.PRIMARY
                    )
            return keyboard

        except Exception as e:
            self.vk_handler.logger.error(f"Ошибка при создании клавиатуры: {e}")
            keyboard = Keyboard(one_time=False, inline=False)
            keyboard.add(
                Text("⚠ Ошибка! В главное меню", payload={"cmd": "main_menu"}),
                color=KeyboardButtonColor.NEGATIVE
            )
            return keyboard