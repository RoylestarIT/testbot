from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.menu import main_menu_keyboard

router = Router(name="settings")

SETTINGS_TEXT = (
    "<b>Настройки</b>\n\n"
    "Подключение API маркетплейсов и tone of voice — в следующих обновлениях."
)


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Авто-публикация ответов (PRO)",
                    callback_data="pro:autopublish",
                ),
            ],
            [InlineKeyboardButton(text="← Главное меню", callback_data="menu:main")],
        ]
    )


@router.callback_query(F.data == "menu:settings")
async def menu_settings(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(SETTINGS_TEXT, reply_markup=settings_keyboard())


@router.callback_query(F.data == "pro:autopublish")
async def pro_autopublish_stub(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "<b>Авто-публикация (PRO)</b>\n\n"
            "Интеграция с Seller API будет доступна на следующем этапе. "
            "Подписка PRO уже даёт безлимитные генерации.",
            reply_markup=settings_keyboard(),
        )
