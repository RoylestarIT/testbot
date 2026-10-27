from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.nav import nav_home_queue
from app.bot.ui import SYNC_BUTTON
from app.services.queue_diagnosis import EmptyQueueReason


def no_cabinets_keyboard() -> InlineKeyboardMarkup:
    from app.bot.keyboards.reviews import reviews_queue_toolbar

    return nav_home_queue(
        extra=[
            reviews_queue_toolbar(include_history=False),
            [
                InlineKeyboardButton(text="🟣 Подключить WB", callback_data="settings:connect:wb"),
                InlineKeyboardButton(text="🔵 Подключить Ozon", callback_data="settings:connect:ozon"),
            ],
        ]
    )


def no_new_reviews_keyboard(reason: EmptyQueueReason | None = None) -> InlineKeyboardMarkup:
    from app.bot.keyboards.reviews import reviews_queue_toolbar

    if reason == EmptyQueueReason.SYNC_ERROR:
        action = [
            InlineKeyboardButton(text="⚙️ Проверить ключ", callback_data="menu:settings"),
            InlineKeyboardButton(text="🛰 Статус", callback_data="menu:service_status"),
        ]
    elif reason == EmptyQueueReason.NEEDS_SYNC:
        action = [
            InlineKeyboardButton(text=SYNC_BUTTON, callback_data="review:sync"),
            InlineKeyboardButton(text="🛰 Статус", callback_data="menu:service_status"),
        ]
    else:
        action = [
            InlineKeyboardButton(text=SYNC_BUTTON, callback_data="review:sync"),
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings"),
        ]
    return nav_home_queue(
        extra=[
            reviews_queue_toolbar(include_history=False),
            action,
        ]
    )


def empty_queue_message(reason: EmptyQueueReason) -> str:
    if reason == EmptyQueueReason.NO_CABINETS:
        return "Подключите кабинет WB или Ozon в ⚙️ Настройки."
    if reason == EmptyQueueReason.SYNC_ERROR:
        return (
            "Очередь пуста, но при последнем обновлении была ошибка.\n"
            "Проверьте ключ в ⚙️ Настройки или откройте 🛰 Статус сервиса."
        )
    if reason == EmptyQueueReason.NEEDS_SYNC:
        return f"Новых отзывов нет — давно не обновляли отзывы. Нажмите «{SYNC_BUTTON}»."
    return "Все новые отзывы обработаны. Отличная работа!"


def poller_notify_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📬  Ответы на отзывы", callback_data="review:mp:list")],
            [InlineKeyboardButton(text="🏠  Сводка", callback_data="menu:dashboard")],
        ]
    )
