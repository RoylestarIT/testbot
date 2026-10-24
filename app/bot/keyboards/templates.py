from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def templates_menu_keyboard(templates: list[dict[str, str]]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for tpl in templates:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🗑 {tpl['label'][:20]}",
                    callback_data=f"settings:tpl:del:{tpl['id']}",
                )
            ]
        )
    if len(templates) < 5:
        rows.append([InlineKeyboardButton(text="➕ Добавить шаблон", callback_data="settings:tpl:add")])
    rows.append([InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
