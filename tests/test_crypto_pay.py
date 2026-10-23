import hashlib
import hmac
import json

from app.services.payment.crypto_pay import (
    build_invoice_payload,
    parse_invoice_payload,
    verify_webhook_signature,
)


def test_invoice_payload_roundtrip() -> None:
    raw = build_invoice_payload(subscription_id=42, user_id=7, plan=__import__("app.db.models", fromlist=["SubscriptionPlan"]).SubscriptionPlan.LITE)
    data = parse_invoice_payload(raw)
    assert data is not None
    assert data["subscription_id"] == 42
    assert data["user_id"] == 7
    assert data["plan"] == "lite"


def test_webhook_signature() -> None:
    token = "123:ABC"
    body = json.dumps({"update_type": "invoice_paid", "payload": {}}).encode()
    secret = hashlib.sha256(token.encode()).digest()
    sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
    assert verify_webhook_signature(token, body, sig) is True
    assert verify_webhook_signature(token, body, "bad") is False
