import httpx
import pytest

from app.db.models import Marketplace, MarketplaceAccount
from app.services.marketplace.wildberries import (
    WildberriesClient,
    WB_FEEDBACKS_ANSWER_PATH,
    WB_FEEDBACKS_LIST_PATH,
    normalize_wb_api_key,
)


def test_normalize_wb_api_key() -> None:
    jwt = "a.b.c"
    assert normalize_wb_api_key(f"Bearer {jwt}") == jwt
    assert normalize_wb_api_key(f"```\n{jwt}\n```") == jwt


@pytest.mark.asyncio
async def test_wb_fetch_pagination() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url.params.get("skip")))
        if request.url.path.endswith(WB_FEEDBACKS_LIST_PATH):
            skip = int(request.url.params.get("skip", "0"))
            if skip == 0:
                items = [{"id": f"id-{i}", "text": f"t{i}", "productValuation": 5} for i in range(100)]
                return httpx.Response(200, json={"data": {"feedbacks": items}})
            items = [{"id": f"id-{i}", "text": f"t{i}", "productValuation": 4} for i in range(100, 120)]
            return httpx.Response(200, json={"data": {"feedbacks": items}})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(base_url="https://feedbacks-api.wildberries.ru", transport=transport)
    wb = WildberriesClient(http_client=client)
    account = MarketplaceAccount(
        user_id=1,
        marketplace=Marketplace.WB,
        encrypted_api_key="dummy",
        is_active=True,
    )
    wb._token = lambda _acc: "token"  # type: ignore[method-assign]

    reviews = await wb.fetch_reviews(account, limit=150, unanswered_only=True)
    assert len(reviews) == 120
    assert calls == ["0", "100"]
    await client.aclose()


@pytest.mark.asyncio
async def test_wb_publish_204() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith(WB_FEEDBACKS_ANSWER_PATH):
            return httpx.Response(204)
        return httpx.Response(200, json={"data": {"feedbacks": []}})

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(base_url="https://feedbacks-api.wildberries.ru", transport=transport)
    wb = WildberriesClient(http_client=client)
    account = MarketplaceAccount(
        user_id=1,
        marketplace=Marketplace.WB,
        encrypted_api_key="k",
        is_active=True,
    )
    wb._token = lambda _acc: "token"  # type: ignore[method-assign]
    await wb.publish_reply(account, "ext-1", "Спасибо!")
    await client.aclose()
