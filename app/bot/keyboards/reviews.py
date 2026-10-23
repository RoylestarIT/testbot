from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import ToneProfile


def reviews_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ответить на отзыв",
                    callback_data="review:manual:start",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Синхронизировать отзывы",
                    callback_data="review:sync",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Новые из маркетплейсов",
                    callback_data="review:mp:list",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="История ответов",
                    callback_data="review:history",
                ),
            ],
            [
                InlineKeyboardButton(text="← Главное меню", callback_data="menu:main"),
            ],
        ]
    )


def rating_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="⭐ 1", callback_data="review:rating:1"),
            InlineKeyboardButton(text="⭐ 2", callback_data="review:rating:2"),
            InlineKeyboardButton(text="⭐ 3", callback_data="review:rating:3"),
        ],
        [
            InlineKeyboardButton(text="⭐ 4", callback_data="review:rating:4"),
            InlineKeyboardButton(text="⭐ 5", callback_data="review:rating:5"),
        ],
        [InlineKeyboardButton(text="Отмена", callback_data="review:cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tone_keyboard(profiles: list[ToneProfile]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for profile in profiles:
        label = profile.description[:40] if profile.description else f"Профиль #{profile.id}"
        rows.append(
            [InlineKeyboardButton(text=label, callback_data=f"review:tone:{profile.id}")]
        )
    rows.append([InlineKeyboardButton(text="Тон по умолчанию", callback_data="review:tone:default")])
    rows.extend(
        [
            [
                InlineKeyboardButton(text="🙏 Благодарность", callback_data="review:tone:preset:grateful"),
                InlineKeyboardButton(text="💬 Извинение", callback_data="review:tone:preset:apology"),
            ],
            [InlineKeyboardButton(text="📎 Нейтрально", callback_data="review:tone:preset:neutral")],
        ]
    )
    rows.append([InlineKeyboardButton(text="Отмена", callback_data="review:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def variants_keyboard(variant_count: int, selected_index: int = 0) -> InlineKeyboardMarkup:
    pick_buttons: list[InlineKeyboardButton] = []
    for index in range(variant_count):
        prefix = "✅ " if index == selected_index else ""
        pick_buttons.append(
            InlineKeyboardButton(
                text=f"{prefix}{index + 1}",
                callback_data=f"review:pick:{index}",
            )
        )

    rows: list[list[InlineKeyboardButton]] = []
    for chunk_start in range(0, len(pick_buttons), 3):
        rows.append(pick_buttons[chunk_start : chunk_start + 3])

    rows.extend(
        [
            [
                InlineKeyboardButton(
                    text="Опубликовать (Lite: скопируй)",
                    callback_data="review:publish",
                ),
            ],
            [
                InlineKeyboardButton(text="Ещё варианты", callback_data="review:more"),
                InlineKeyboardButton(text="Изменить тон", callback_data="review:change_tone"),
            ],
            [InlineKeyboardButton(text="← Главное меню", callback_data="menu:main")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
