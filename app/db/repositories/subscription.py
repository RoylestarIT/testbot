from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PaymentMethod, Subscription, SubscriptionPlan, SubscriptionStatus


class SubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, subscription_id: int) -> Subscription | None:
        return await self._session.get(Subscription, subscription_id)

    async def get_by_telegram_charge_id(self, charge_id: str) -> Subscription | None:
        result = await self._session.execute(
            select(Subscription)
            .where(
                Subscription.external_payment_id == charge_id,
                Subscription.payment_method.in_((PaymentMethod.STARS, PaymentMethod.TELEGRAM)),
            )
            .limit(1)
        )
        return result.scalars().first()

    async def list_by_user_id(self, user_id: int) -> list[Subscription]:
        result = await self._session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.id.desc())
        )
        return list(result.scalars().all())

    async def list_pending(self, *, limit: int = 50) -> list[Subscription]:
        result = await self._session.execute(
            select(Subscription)
            .where(Subscription.status == SubscriptionStatus.PENDING)
            .order_by(Subscription.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_active_for_user(self, user_id: int) -> Subscription | None:
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
                or_(Subscription.expires_at.is_(None), Subscription.expires_at > now),
            )
            .order_by(Subscription.id.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def create(
        self,
        *,
        user_id: int,
        plan: SubscriptionPlan,
        status: SubscriptionStatus,
        expires_at: datetime | None = None,
        payment_method: PaymentMethod | None = None,
        external_payment_id: str | None = None,
    ) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            status=status,
            expires_at=expires_at,
            payment_method=payment_method,
            external_payment_id=external_payment_id,
        )
        self._session.add(subscription)
        await self._session.flush()
        await self._session.refresh(subscription)
        return subscription
