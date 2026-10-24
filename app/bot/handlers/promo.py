from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu_keyboard
from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.session import get_session_factory
from app.services.promo import redeem_promo_code

router = Router(name="promo")


@router.message(Command("promo"))
async def cmd_promo(message: Message, command: CommandObject, db_user: DbUser) -> None:
    code = (command.args or "").strip()
    if not code:
        await message.answer("Использование: /promo КОД")
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        ok, text = await redeem_promo_code(session, db_user.id, code)
        await session.commit()
    tg_id = message.from_user.id if message.from_user else 0
    await message.answer(
        text,
        reply_markup=main_menu_keyboard(show_admin=tg_id in get_settings().admin_ids),
    )
