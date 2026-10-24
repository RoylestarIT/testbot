from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

import httpx
from loguru import logger

from app.core.config import Settings, get_settings
from app.db.models import SubscriptionPlan

CRYPTO_PAY_MAINNET = "https://pay.crypt.bot/api"
CRYPTO_PAY_TESTNET = "https://testnet-pay.crypt.bot/api"


class CryptoPayError(Exception):
    pass


def crypto_pay_enabled(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    return bool(settings.crypto_pay_api_token.strip())


def _api_base(settings: Settings) -> str:
    if settings.crypto_pay_testnet:
        return CRYPTO_PAY_TESTNET
    return CRYPTO_PAY_MAINNET


def _headers(settings: Settings) -> dict[str, str]:
    return {"Crypto-Pay-API-Token": settings.crypto_pay_api_token.strip()}


async def _api_request(settings: Settings, method: str, **params: Any) -> Any:
    url = f"{_api_base(settings)}/{method}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=_headers(settings), params=params)
    data = response.json()
    if not data.get("ok"):
        raise CryptoPayError(str(data.get("error", response.text)))
    return data.get("result")


def verify_webhook_signature(token: str, body_raw: bytes, signature_header: str | None) -> bool:
    if not signature_header:
        return False
    secret = hashlib.sha256(token.encode()).digest()
    expected = hmac.new(secret, body_raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header.strip())


def crypto_amount_for_plan(settings: Settings, plan: SubscriptionPlan) -> str:
    if plan == SubscriptionPlan.PRO:
        return settings.crypto_pro_amount_usd
    return settings.crypto_lite_amount_usd


def crypto_price_label(settings: Settings, plan: SubscriptionPlan) -> str:
    """Сумма счёта Crypto Pay (fiat USD) — в UI показываем как USDT."""
    amount = crypto_amount_for_plan(settings, plan).strip()
    return f"{amount} USDT"


def build_invoice_payload(*, subscription_id: int, user_id: int, plan: SubscriptionPlan) -> str:
    return json.dumps(
        {"subscription_id": subscription_id, "user_id": user_id, "plan": plan.value},
        separators=(",", ":"),
    )


def parse_invoice_payload(payload: str | None) -> dict[str, Any] | None:
    if not payload:
        return None
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


async def create_subscription_invoice(
    settings: Settings,
    *,
    subscription_id: int,
    user_id: int,
    plan: SubscriptionPlan,
) -> dict[str, Any]:
    amount = crypto_amount_for_plan(settings, plan)
    title = "ReviewPilot PRO" if plan == SubscriptionPlan.PRO else "ReviewPilot Lite"
    result = await _api_request(
        settings,
        "createInvoice",
        currency_type="fiat",
        fiat="USD",
        amount=amount,
        description=f"{title} · 1 месяц",
        payload=build_invoice_payload(subscription_id=subscription_id, user_id=user_id, plan=plan),
        expires_in=3600,
        allow_comments=False,
    )
    if not isinstance(result, dict):
        raise CryptoPayError("Unexpected createInvoice response")
    return result


async def get_invoice(settings: Settings, invoice_id: int) -> dict[str, Any] | None:
    result = await _api_request(settings, "getInvoices", invoice_ids=str(invoice_id))
    if isinstance(result, dict) and "items" in result:
        items = result["items"]
    elif isinstance(result, list):
        items = result
    else:
        items = []
    if not items:
        return None
    item = items[0]
    return item if isinstance(item, dict) else None
