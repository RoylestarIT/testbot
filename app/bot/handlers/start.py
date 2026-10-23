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
    "• <b>Отзывы</b> — ручной ввод и генерация ответов (Lite).\n"
    "• <b>Настройки</b> — ключи API и tone of voice (скоро).\n"
    "• <b>Подписка</b> — Lite / PRO, Stars и QR (РБ).\n\n"
    "Команды: /start — меню, /my_subscription — статус подписки."
)

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "menu:help")
async def menu_help(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(HELP_TEXT, reply_markup=main_menu_keyboard())


