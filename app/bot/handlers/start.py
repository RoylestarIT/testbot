from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.menu import main_menu_keyboard

router = Router(name="start")

WELCOME_TEXT = (
    "<b>ReviewPilot</b> — помощник селлера для ответов на отзывы "
    "Wildberries и Ozon.\n\n"
    "• <b>Lite (FREE)</b> — бот предлагает варианты ответа, вы публикуете сами.\n"
    "• <b>PRO</b> — отправка ответа через Seller API по кнопке «Отправить».\n\n"
    "Мы не аффилированы с маркетплейсами и не обещаем рост рейтинга.\n"
    "Выберите раздел в меню:"
)

HELP_TEXT = (
    "<b>Помощь</b>\n\n"
    "• <b>Отзывы</b> — просмотр и генерация ответов (скоро).\n"
    "• <b>Настройки</b> — ключи API и tone of voice (скоро).\n"
    "• <b>Подписка</b> — Lite и PRO (скоро).\n\n"
    "Команда /start — вернуться в главное меню."
)

STUB_TEXT = "Раздел в разработке. Скоро будет доступен."


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "menu:help")
async def menu_help(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(F.data.in_({"menu:reviews", "menu:settings", "menu:subscription"}))
async def menu_stub(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            f"{STUB_TEXT}\n\n{WELCOME_TEXT}",
            reply_markup=main_menu_keyboard(),
        )
