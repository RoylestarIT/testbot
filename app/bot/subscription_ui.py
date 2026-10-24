"""Экраны подписки — одна точка входа, без простыней."""

from __future__ import annotations

from app.bot.ui import brand_title, bullet, muted, quote
from app.constants import FREE_DAILY_GENERATIONS
from app.db.models import Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.services.payment.fx_rates import SubscriptionPricing
from app.services.access_messaging import build_my_access_publish_block
from app.services.pro_access import trial_pro_active
from app.services.subscription import plan_label, status_label

SUBSCRIPTION_SEP = "───────────────"


def build_subscription_hub(
    pricing: SubscriptionPricing,
    *,
    access_line: str,
    trial_line: str | None = None,
) -> str:
    lines = [
        f"{brand_title('Подписка', tagline='Фикс в месяц · WB/Ozon', icon='💎').strip()}",
        SUBSCRIPTION_SEP,
        "",
        quote(f"👤  {access_line}"),
        "",
        f"✨  Lite — {pricing.lite_price_label()}",
        f"🚀  PRO — {pricing.pro_price_label()}",
        "",
        muted("Оплата: Stars · крипта · карта РФ/РБ · СБП/перевод"),
    ]
    if trial_line:
        lines.extend(["", trial_line])
    return "\n".join(lines)


def build_payment_hub(pricing: SubscriptionPricing) -> str:
    return (
        f"{brand_title('Оплата', tagline='Выберите способ', icon='💳').strip()}\n"
        f"{SUBSCRIPTION_SEP}\n\n"
        f"✨  Lite — {pricing.lite_price_label()}\n"
        f"🚀  PRO — {pricing.pro_price_label()}\n\n"
        f"{muted('После оплаты проверьте «Мой доступ».')}"
    )


def build_my_access_text(
    user: User,
    subscription: Subscription | None,
    *,
    generations_remaining: int | None,
    access_tier_line: str | None,
) -> str:
    lines = [
        f"{brand_title('Мой доступ', icon='👤').strip()}",
        SUBSCRIPTION_SEP,
        "",
    ]
    if access_tier_line:
        lines.append(f"📌  <b>{access_tier_line}</b>")
        lines.append("")

    trial_active = trial_pro_active(user)

    if subscription is None:
        lines.extend(
            [
                bullet("Оплаченная подписка: <b>нет</b>"),
                bullet(
                    f"Генераций сегодня: <b>{generations_remaining if generations_remaining is not None else '—'}</b> / {FREE_DAILY_GENERATIONS}"
                ),
            ]
        )
        lines.extend(build_my_access_publish_block(user, subscription, trial_active=trial_active))
        lines.extend(["", muted("Оформить: «Подписка → Оплатить»")])
    else:
        expires = (
            subscription.expires_at.strftime("%d.%m.%Y")
            if subscription.expires_at
            else "—"
        )
        lines.extend(
            [
                bullet(f"План: <b>{plan_label(subscription.plan)}</b> · {status_label(subscription.status)}"),
                bullet(f"До: <b>{expires}</b>"),
            ]
        )
        if subscription.status == SubscriptionStatus.ACTIVE:
            lines.extend(build_my_access_publish_block(user, subscription, trial_active=trial_active))
        elif generations_remaining is not None:
            lines.append(bullet(f"Генераций сегодня: <b>{generations_remaining}</b> / {FREE_DAILY_GENERATIONS}"))
        if subscription.status == SubscriptionStatus.PENDING:
            lines.append("")
            lines.append(muted("⏳ Ожидает подтверждения оплаты."))

    lines.extend(["", muted(f"ID для поддержки: <code>{user.tg_id}</code>")])
    return "\n".join(lines)
