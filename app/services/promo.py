from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.promo_code import PromoCodeRepository
from app.db.repositories.user import UserRepository
from app.services.pro_access import admin_extend_trial


async def redeem_promo_code(session: AsyncSession, user_id: int, raw_code: str) -> tuple[bool, str]:
    code = raw_code.strip()
    if len(code) < 3:
        return False, "Введите промокод."

    repo = PromoCodeRepository(session)
    promo = await repo.get_by_code(code)
    if promo is None or not promo.is_active:
        return False, "Промокод не найден или не активен."
    if promo.redemption_count >= promo.max_redemptions:
        return False, "Лимит активаций промокода исчерпан."
    if await repo.user_redeemed(user_id, promo.id):
        return False, "Вы уже использовали этот промокод."

    user = await admin_extend_trial(session, user_id, promo.trial_days)
    if user is None:
        return False, "Пользователь не найден."

    await repo.redeem(user_id, promo)
    await session.flush()
    until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
    return True, f"🎁 Промокод применён: Trial PRO до <b>{until}</b> (+{promo.trial_days} дн.)."
