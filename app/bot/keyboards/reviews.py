from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import ToneProfile


def reviews_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="→  Ручной ответ", callback_data="review:manual:start")],
            [InlineKeyboardButton(text="→  Синхронизация", callback_data="review:sync")],
            [InlineKeyboardButton(text="→  Очередь WB/Ozon", callback_data="review:mp:list")],
            [InlineKeyboardButton(text="→  История", callback_data="review:history")],
            [InlineKeyboardButton(text="←  Сводка", callback_data="menu:main")],
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
        [InlineKeyboardButton(text="←  Отмена", callback_data="review:cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tone_keyboard(profiles: list[ToneProfile]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if not profiles:
        rows.append(
            [InlineKeyboardButton(text="→  Создать tone", callback_data="settings:tone:add")]
        )
    for profile in profiles:
        label = profile.description[:40] if profile.description else f"Профиль #{profile.id}"
        rows.append(
            [InlineKeyboardButton(text=label, callback_data=f"review:tone:{profile.id}")]
        )
    rows.append([InlineKeyboardButton(text="→  Стандартный тон", callback_data="review:tone:default")])
    rows.extend(
        [
            [
                InlineKeyboardButton(text="Благодарность", callback_data="review:tone:preset:grateful"),
                InlineKeyboardButton(text="Извинение", callback_data="review:tone:preset:apology"),
            ],
            [InlineKeyboardButton(text="Нейтрально", callback_data="review:tone:preset:neutral")],
        ]
    )
    rows.append([InlineKeyboardButton(text="←  Отмена", callback_data="review:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def variants_keyboard(
    variant_count: int,
    selected_index: int = 0,
    *,
    can_publish: bool = False,
    review_id: int | None = None,
    show_quick_templates: bool = False,
    has_next_in_queue: bool = False,
    mp_mode: bool = False,
) -> InlineKeyboardMarkup:
    pick_buttons: list[InlineKeyboardButton] = []
    for index in range(variant_count):
        prefix = "● " if index == selected_index else ""
        pick_buttons.append(
            InlineKeyboardButton(
                text=f"{prefix}{index + 1}",
                callback_data=f"review:pick:{index}",
            )
        )

    rows: list[list[InlineKeyboardButton]] = []
    for chunk_start in range(0, len(pick_buttons), 3):
        rows.append(pick_buttons[chunk_start : chunk_start + 3])

    if show_quick_templates:
        rows.append(
            [
                InlineKeyboardButton(text="⚡ Спасибо!", callback_data="review:quick:thanks"),
                InlineKeyboardButton(text="⚡ Рады!", callback_data="review:quick:glad"),
            ]
        )

    copy_cb = "review:mp:copy" if mp_mode else "review:publish"
    edit_cb = "review:mp:edit" if mp_mode else "review:edit"
    action_row = [
        InlineKeyboardButton(text="→  Копировать", callback_data=copy_cb),
        InlineKeyboardButton(text="→  Править", callback_data=edit_cb),
    ]
    if can_publish and review_id is not None:
        action_row.append(
            InlineKeyboardButton(
                text="→  Publish",
                callback_data=f"review:mp:publish:{review_id}",
            )
        )
    rows.append(action_row)
    rows.append(
        [
            InlineKeyboardButton(text="↻  Ещё", callback_data="review:more"),
            InlineKeyboardButton(text="↻  Тон", callback_data="review:change_tone"),
        ]
    )
    if has_next_in_queue:
        rows.append([InlineKeyboardButton(text="→  Следующий", callback_data="review:mp:next")])
    rows.append([InlineKeyboardButton(text="←  Сводка", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def history_filter_keyboard(
    *,
    current: str,
    account_id: int | None,
    accounts: list,
) -> InlineKeyboardMarkup:
    def _status_btn(label: str, key: str) -> InlineKeyboardButton:
        prefix = "• " if current == key else ""
        return InlineKeyboardButton(text=f"{prefix}{label}", callback_data=f"review:history:filter:{key}")

    rows: list[list[InlineKeyboardButton]] = [
        [
            _status_btn("Все", "all"),
            _status_btn("Publish", "published"),
            _status_btn("Копия", "copied"),
        ],
    ]
    if accounts:
        acc_row: list[InlineKeyboardButton] = []
        if account_id is None:
            acc_row.append(InlineKeyboardButton(text="• Все кабинеты", callback_data="review:history:acc:0"))
        else:
            acc_row.append(InlineKeyboardButton(text="Все кабинеты", callback_data="review:history:acc:0"))
        for acc in accounts[:4]:
            mp = "WB" if acc.marketplace.value == "wb" else "Oz"
            name = (acc.shop_name or f"{mp}#{acc.id}")[:12]
            mark = "• " if account_id == acc.id else ""
            acc_row.append(
                InlineKeyboardButton(
                    text=f"{mark}{name}",
                    callback_data=f"review:history:acc:{acc.id}",
                )
            )
        rows.append(acc_row)
    rows.append([InlineKeyboardButton(text="← Отзывы", callback_data="menu:reviews")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
