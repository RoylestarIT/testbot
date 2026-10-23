from aiogram import Router

from app.bot.handlers import admin, marketplace_reviews, reviews, settings, start, subscription
from app.bot.middlewares.pro_subscription import ProSubscriptionMiddleware
from app.bot.middlewares.subscription_check import SubscriptionCheckMiddleware

main_router = Router(name="main")
main_router.include_router(start.router)
main_router.include_router(subscription.router)
main_router.include_router(admin.router)
main_router.include_router(settings.router)
main_router.include_router(marketplace_reviews.router)
main_router.include_router(reviews.router)

reviews.router.callback_query.middleware(SubscriptionCheckMiddleware())
settings.router.callback_query.middleware(ProSubscriptionMiddleware())

__all__ = ["main_router"]
