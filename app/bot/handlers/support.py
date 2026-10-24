from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.bot.support_ui import support_keyboard, support_screen_text

router = Router(name="support")


@router.callback_query(F.data == "menu:support")
async def menu_support(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(support_screen_text(), reply_markup=support_keyboard())
