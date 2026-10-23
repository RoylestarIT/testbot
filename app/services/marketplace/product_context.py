from __future__ import annotations

from typing import Any

from app.db.models import Marketplace


def product_context_for_llm(
    raw: dict[str, Any] | None,
    marketplace: Marketplace | None,
) -> str | None:
    """Краткий контекст товара для промпта LLM (из raw_json sync)."""
    if not raw or raw.get("source") == "manual":
        return None

    parts: list[str] = []

    if marketplace == Marketplace.WB:
        name = raw.get("productName") or raw.get("productDetails", {}).get("productName")
        if isinstance(name, str) and name.strip():
            parts.append(f"Название: {name.strip()[:160]}")
        nm = raw.get("nmId") or raw.get("productDetails", {}).get("nmId")
        if nm is not None:
            parts.append(f"Артикул WB (nmId): {nm}")
        brand = raw.get("brandName") or raw.get("productDetails", {}).get("brandName")
        if isinstance(brand, str) and brand.strip():
            parts.append(f"Бренд: {brand.strip()[:80]}")
    elif marketplace == Marketplace.OZON:
        sku = raw.get("sku")
        if sku is not None:
            parts.append(f"SKU Ozon: {sku}")
        name = raw.get("product_name") or raw.get("productName")
        if isinstance(name, str) and name.strip():
            parts.append(f"Название: {name.strip()[:160]}")

    if not parts:
        return None
    return "; ".join(parts)


def product_hint_short(
    raw: dict[str, Any] | None,
    marketplace: Marketplace | None,
) -> str | None:
    """Одна строка для карточки отзыва в UI."""
    ctx = product_context_for_llm(raw, marketplace)
    if ctx is None:
        return None
    if len(ctx) > 120:
        return ctx[:117] + "…"
    return ctx
