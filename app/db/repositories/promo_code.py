from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PromoCode, PromoRedemption


class PromoCodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_code(self, code: str) -> PromoCode | None:
        normalized = code.strip().upper()
        result = await self._session.execute(select(PromoCode).where(PromoCode.code == normalized))
        return result.scalar_one_or_none()

    async def create(self, *, code: str, trial_days: int, max_redemptions: int) -> PromoCode:
        promo = PromoCode(
            code=code.strip().upper(),
            trial_days=trial_days,
            max_redemptions=max_redemptions,
        )
        self._session.add(promo)
        await self._session.flush()
        await self._session.refresh(promo)
        return promo

    async def list_active(self, limit: int = 20) -> list[PromoCode]:
        result = await self._session.execute(
            select(PromoCode).where(PromoCode.is_active.is_(True)).order_by(PromoCode.id.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def user_redeemed(self, user_id: int, promo_id: int) -> bool:
        result = await self._session.execute(
            select(PromoRedemption.id).where(
                PromoRedemption.user_id == user_id,
                PromoRedemption.promo_code_id == promo_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def redeem(self, user_id: int, promo: PromoCode) -> PromoRedemption:
        promo.redemption_count += 1
        row = PromoRedemption(user_id=user_id, promo_code_id=promo.id)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row
