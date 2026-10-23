from aiogram import Router

from app.bot.handlers import start

main_router = Router(name="main")
main_router.include_router(start.router)

__all__ = ["main_router"]
