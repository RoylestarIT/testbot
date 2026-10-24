#!/usr/bin/env python3
"""Smoke-test Ozon unanswered-questions API for the first active Ozon cabinet."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.core.config import get_settings
from app.db.models import Marketplace, MarketplaceAccount
from app.db.session import get_session_factory
from app.services.marketplace.ozon import OzonClient, MarketplaceAPIError


async def main() -> None:
    settings = get_settings()
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(
            select(MarketplaceAccount).where(
                MarketplaceAccount.marketplace == Marketplace.OZON,
                MarketplaceAccount.is_active.is_(True),
            )
        )
        account = result.scalars().first()
    if account is None:
        print("No active Ozon marketplace account in DB — skip live check.")
        return

    client = OzonClient()
    try:
        items = await client.list_unanswered_questions(account, limit=5)
        print(f"Ozon questions API OK: {len(items)} item(s) returned (limit 5).")
    except MarketplaceAPIError as exc:
        if exc.status_code == 404:
            print(
                "Ozon returned 404 for question list — API not available for this seller "
                "(expected limitation, not a bot bug)."
            )
        else:
            raise
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
