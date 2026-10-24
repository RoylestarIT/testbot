from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
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
        SubscriptionStatus.EXPIRED: "истёкла",
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


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


async def _renewal_start(session: AsyncSession, subscription: Subscription, now: datetime) -> datetime:
    """Same-plan renewal continues from the current expiry so prepaid days are kept."""
    current = await get_effective_subscription(session, subscription.user_id)
    if (
        current is None
        or current.id == subscription.id
        or current.plan != subscription.plan
        or current.expires_at is None
    ):
        return now
    return max(now, _as_utc(current.expires_at))


async def activate_subscription(
    session: AsyncSession,
    subscription: Subscription,
    *,
    external_payment_id: str | None = None,
) -> Subscription:
    now = datetime.now(UTC)
    starts_at = await _renewal_start(session, subscription, now)
    await expire_active_subscriptions(session, subscription.user_id)
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.expires_at = starts_at + timedelta(days=SUBSCRIPTION_PERIOD_DAYS)
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
    """Idempotent per charge id: a redelivered successful_payment returns the existing row."""
    repo = SubscriptionRepository(session)
    existing = await repo.get_by_telegram_charge_id(telegram_payment_charge_id)
    if existing is not None:
        return existing
    try:
        async with session.begin_nested():
            subscription = await repo.create(
                user_id=user_id,
                plan=plan,
                status=SubscriptionStatus.PENDING,
                payment_method=payment_method,
                external_payment_id=telegram_payment_charge_id,
            )
    except IntegrityError:
        existing = await repo.get_by_telegram_charge_id(telegram_payment_charge_id)
        if existing is None:
            raise
        return existing
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


async def grant_subscription_by_tg_id(
    session: AsyncSession,
    *,
    tg_id: int,
    plan: SubscriptionPlan,
) -> tuple[Subscription | None, str | None]:
    from app.db.repositories.user import UserRepository

    user = await UserRepository(session).get_by_tg_id(tg_id)
    if user is None:
        return None, "Пользователь не найден. Попросите его отправить /start боту."
    repo = SubscriptionRepository(session)
    subscription = await repo.create(
        user_id=user.id,
        plan=plan,
        status=SubscriptionStatus.PENDING,
        payment_method=PaymentMethod.QR,
        external_payment_id=f"admin-grant-{datetime.now(UTC).timestamp():.0f}",
    )
    activated = await activate_subscription(session, subscription)
    return activated, None


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
    return await approve_pending_subscription(session, subscription_id)


async def create_crypto_pending(
    session: AsyncSession,
    *,
    user_id: int,
    plan: SubscriptionPlan,
) -> Subscription:
    repo = SubscriptionRepository(session)
    for existing in await repo.list_by_user_id(user_id):
        # A row that already has an invoice stays bound to it: the user may still pay the old link.
        if (
            existing.status == SubscriptionStatus.PENDING
            and existing.payment_method == PaymentMethod.CRYPTO
            and existing.plan == plan
            and not existing.external_payment_id
        ):
            return existing
    return await repo.create(
        user_id=user_id,
        plan=plan,
        status=SubscriptionStatus.PENDING,
        payment_method=PaymentMethod.CRYPTO,
    )


async def approve_pending_subscription(session: AsyncSession, subscription_id: int) -> Subscription | None:
    repo = SubscriptionRepository(session)
    subscription = await repo.get_by_id(subscription_id)
    if subscription is None:
        return None
    if subscription.status != SubscriptionStatus.PENDING:
        return None
    if subscription.payment_method not in (PaymentMethod.QR, PaymentMethod.CRYPTO):
        return None
    return await activate_subscription(session, subscription)


async def activate_from_crypto_invoice(
    session: AsyncSession,
    *,
    subscription_id: int,
    invoice_id: str,
) -> Subscription | None:
    # Webhook, background poller and the "check payment" button can race; the conditional
    # UPDATE row-locks in PostgreSQL so only one caller gets rowcount == 1.
    claimed = await session.execute(
        update(Subscription)
        .where(
            Subscription.id == subscription_id,
            Subscription.status == SubscriptionStatus.PENDING,
            Subscription.payment_method == PaymentMethod.CRYPTO,
        )
        .values(external_payment_id=invoice_id)
    )
    if claimed.rowcount != 1:
        return None
    subscription = await SubscriptionRepository(session).get_by_id(subscription_id)
    if subscription is None:
        return None
    return await activate_subscription(
        session,
        subscription,
        external_payment_id=invoice_id,
    )


def format_subscription_summary(
    user: User,
    subscription: Subscription | None,
    *,
    generations_remaining: int | None = None,
    access_tier_line: str | None = None,
) -> str:
    lines = ["👤 <b>Ваш доступ</b>", f"🆔 Telegram ID: <code>{user.tg_id}</code>", ""]
    if access_tier_line:
        lines.append(access_tier_line)
        lines.append("")

    if subscription is None:
        lines.extend(
            [
                "Оплаченная подписка: <b>нет</b>",
                f"Генераций сегодня: <b>{generations_remaining if generations_remaining is not None else '—'}</b> из 5",
                "Publish в WB/Ozon из бота: <b>только PRO</b> (или trial / бесплатная квота)",
                "",
                "Лимиты бесплатного тарифа: 1 кабинет WB/Ozon, 1 tone-профиль.\n"
                "Оформите Lite или PRO — «Подписка → Оплатить».",
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
            f"Подписка: <b>{plan_label(subscription.plan)}</b>",
            f"Статус: {status_label(subscription.status)}",
            f"Оплата: {subscription.payment_method.value if subscription.payment_method else '—'}",
            f"Действует до: {expires}",
        ]
    )

    if subscription.status == SubscriptionStatus.ACTIVE:
        if subscription.plan == SubscriptionPlan.PRO:
            lines.append("Генерации: <b>без лимита</b>")
            lines.append("Publish в API + авто-ответы 4–5★: <b>да</b>")
        else:
            lines.append("Генерации: <b>без лимита</b>")
            lines.append("Publish в API: <b>нет</b> — используйте «Скопировать ответ»")
    elif generations_remaining is not None:
        lines.append(f"Генераций сегодня (бесплатно): <b>{generations_remaining}</b> из 5")

    if subscription.status == SubscriptionStatus.PENDING:
        lines.append("")
        lines.append("Заявка на оплату QR ожидает подтверждения администратором.")

    return "\n".join(lines)
