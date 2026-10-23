from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    PaymentMethod,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
)
from app.db.repositories.subscription import SubscriptionRepository

SUBSCRIPTION_PERIOD_DAYS = 30


def plan_label(plan: SubscriptionPlan) -> str:
    if plan == SubscriptionPlan.PRO:
        return "PRO"
    return "Lite"


def status_label(status: SubscriptionStatus) -> str:
    mapping = {
        SubscriptionStatus.ACTIVE: "активна",
        SubscriptionStatus.PENDING: "ожидает подтверждения",
        SubscriptionStatus.EXPIRED: "истекла",
    }
    return mapping.get(status, status.value)


async def get_effective_subscription(session: AsyncSession, user_id: int) -> Subscription | None:
    return await SubscriptionRepository(session).get_active_for_user(user_id)


async def expire_active_subscriptions(session: AsyncSession, user_id: int) -> None:
    repo = SubscriptionRepository(session)
    now = datetime.now(UTC)
    for subscription in await repo.list_by_user_id(user_id):
        if subscription.status == SubscriptionStatus.ACTIVE:
            subscription.status = SubscriptionStatus.EXPIRED
            if subscription.expires_at is None:
                subscription.expires_at = now
    await session.flush()


async def activate_subscription(
    session: AsyncSession,
    subscription: Subscription,
    *,
    external_payment_id: str | None = None,
) -> Subscription:
    await expire_active_subscriptions(session, subscription.user_id)
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.expires_at = datetime.now(UTC) + timedelta(days=SUBSCRIPTION_PERIOD_DAYS)
    if external_payment_id:
        subscription.external_payment_id = external_payment_id
    await session.flush()
    await session.refresh(subscription)
    return subscription


async def activate_from_telegram_invoice(
    session: AsyncSession,
    *,
    user_id: int,
    plan: SubscriptionPlan,
    telegram_payment_charge_id: str,
    payment_method: PaymentMethod,
) -> Subscription:
    repo = SubscriptionRepository(session)
    subscription = await repo.create(
        user_id=user_id,
        plan=plan,
        status=SubscriptionStatus.PENDING,
        payment_method=payment_method,
        external_payment_id=telegram_payment_charge_id,
    )
    return await activate_subscription(
        session,
        subscription,
        external_payment_id=telegram_payment_charge_id,
    )


async def activate_from_stars(
    session: AsyncSession,
    *,
    user_id: int,
    plan: SubscriptionPlan,
    telegram_payment_charge_id: str,
) -> Subscription:
    return await activate_from_telegram_invoice(
        session,
        user_id=user_id,
        plan=plan,
        telegram_payment_charge_id=telegram_payment_charge_id,
        payment_method=PaymentMethod.STARS,
    )


async def create_qr_pending(
    session: AsyncSession,
    *,
    user_id: int,
    plan: SubscriptionPlan,
) -> Subscription:
    repo = SubscriptionRepository(session)
    for existing in await repo.list_by_user_id(user_id):
        if (
            existing.status == SubscriptionStatus.PENDING
            and existing.payment_method == PaymentMethod.QR
            and existing.plan == plan
        ):
            return existing
    return await repo.create(
        user_id=user_id,
        plan=plan,
        status=SubscriptionStatus.PENDING,
        payment_method=PaymentMethod.QR,
    )


async def reject_qr_subscription(session: AsyncSession, subscription_id: int) -> Subscription | None:
    repo = SubscriptionRepository(session)
    subscription = await repo.get_by_id(subscription_id)
    if subscription is None:
        return None
    if subscription.status != SubscriptionStatus.PENDING:
        return None
    subscription.status = SubscriptionStatus.EXPIRED
    await session.flush()
    await session.refresh(subscription)
    return subscription


async def approve_qr_subscription(session: AsyncSession, subscription_id: int) -> Subscription | None:
    repo = SubscriptionRepository(session)
    subscription = await repo.get_by_id(subscription_id)
    if subscription is None:
        return None
    if subscription.status != SubscriptionStatus.PENDING:
        return None
    if subscription.payment_method != PaymentMethod.QR:
        return None
    return await activate_subscription(session, subscription)


def format_subscription_summary(
    user: User,
    subscription: Subscription | None,
    *,
    generations_remaining: int | None = None,
) -> str:
    lines = ["<b>Ваша подписка</b>", f"Telegram ID: <code>{user.tg_id}</code>", ""]

    if subscription is None:
        lines.extend(
            [
                "Тариф: <b>Lite (бесплатный)</b>",
                f"Лимит: {generations_remaining if generations_remaining is not None else '—'} "
                "генераций сегодня (из 5).",
                "",
                "Оформите Lite или PRO в разделе «Подписка».",
            ]
        )
        return "\n".join(lines)

    expires = (
        subscription.expires_at.strftime("%d.%m.%Y %H:%M UTC")
        if subscription.expires_at
        else "—"
    )
    lines.extend(
        [
            f"Тариф: <b>{plan_label(subscription.plan)}</b>",
            f"Статус: {status_label(subscription.status)}",
            f"Оплата: {subscription.payment_method.value if subscription.payment_method else '—'}",
            f"Действует до: {expires}",
        ]
    )

    if subscription.status == SubscriptionStatus.ACTIVE and subscription.plan == SubscriptionPlan.PRO:
        lines.append("Генерации: <b>без лимита</b>")
    elif generations_remaining is not None:
        lines.append(f"Генераций сегодня осталось: <b>{generations_remaining}</b>")

    if subscription.status == SubscriptionStatus.PENDING:
        lines.append("")
        lines.append("Заявка на оплату QR ожидает подтверждения администратором.")

    return "\n".join(lines)
