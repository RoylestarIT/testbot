from aiogram import Router

from app.bot.handlers import reviews, start
from app.bot.middlewares.subscription_check import SubscriptionCheckMiddleware

main_router = Router(name="main")
main_router.include_router(start.router)
main_router.include_router(reviews.router)

reviews.router.callback_query.middleware(SubscriptionCheckMiddleware())

__all__ = ["main_router"]
