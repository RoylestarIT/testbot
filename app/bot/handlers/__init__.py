from aiogram import Router

from app.bot.handlers import (
    admin,
    dashboard,
    marketplace_reviews,
    onboarding,
    reviews,
    settings,
    start,
    subscription,
    support,
)
from app.bot.middlewares.pro_subscription import ProSubscriptionMiddleware
from app.bot.middlewares.subscription_check import SubscriptionCheckMiddleware

main_router = Router(name="main")
main_router.include_router(start.router)
main_router.include_router(dashboard.router)
main_router.include_router(onboarding.router)
main_router.include_router(support.router)
main_router.include_router(subscription.router)
main_router.include_router(admin.router)
main_router.include_router(settings.router)
main_router.include_router(marketplace_reviews.router)
main_router.include_router(reviews.router)

reviews.router.callback_query.middleware(SubscriptionCheckMiddleware())
settings.router.callback_query.middleware(ProSubscriptionMiddleware())

__all__ = ["main_router"]
