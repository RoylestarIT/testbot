from functools import lru_cache

from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    bot_short_description: str = Field(default="", validation_alias="BOT_SHORT_DESCRIPTION")
    bot_description: str = Field(default="", validation_alias="BOT_DESCRIPTION")
    bot_profile_language: str = Field(default="ru", validation_alias="BOT_PROFILE_LANGUAGE")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./reviewpilot.db",
        validation_alias="DATABASE_URL",
    )
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias="OPENAI_BASE_URL",
    )
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    fernet_key: str = Field(default="", validation_alias="FERNET_KEY")
    admin_ids: Annotated[list[int], NoDecode] = Field(
        default_factory=list,
        validation_alias="ADMIN_IDS",
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    payment_provider_token: str = Field(default="", validation_alias="PAYMENT_PROVIDER_TOKEN")
    payment_enable_stars: bool = Field(default=False, validation_alias="PAYMENT_ENABLE_STARS")
    crypto_pay_api_token: str = Field(default="", validation_alias="CRYPTO_PAY_API_TOKEN")
    crypto_pay_testnet: bool = Field(default=False, validation_alias="CRYPTO_PAY_TESTNET")
    crypto_lite_amount_usd: str = Field(default="10", validation_alias="CRYPTO_LITE_AMOUNT_USD")
    crypto_pro_amount_usd: str = Field(default="20", validation_alias="CRYPTO_PRO_AMOUNT_USD")
    crypto_pay_webhook_path: str = Field(default="/cryptopay/webhook", validation_alias="CRYPTO_PAY_WEBHOOK_PATH")
    payment_currency: str = Field(default="RUB", validation_alias="PAYMENT_CURRENCY")
    subscription_lite_price_rub: int = Field(default=800, validation_alias="SUBSCRIPTION_LITE_PRICE_RUB")
    subscription_pro_price_rub: int = Field(default=1600, validation_alias="SUBSCRIPTION_PRO_PRICE_RUB")
    subscription_lite_price_byn: float = Field(default=30.0, validation_alias="SUBSCRIPTION_LITE_PRICE_BYN")
    subscription_pro_price_byn: float = Field(default=60.0, validation_alias="SUBSCRIPTION_PRO_PRICE_BYN")
    subscription_lite_price_minor: int = Field(
        default=80000,
        validation_alias="SUBSCRIPTION_LITE_PRICE_MINOR",
    )
    subscription_pro_price_minor: int = Field(
        default=160000,
        validation_alias="SUBSCRIPTION_PRO_PRICE_MINOR",
    )
    subscription_lite_stars: int = Field(default=750, validation_alias="SUBSCRIPTION_LITE_STARS")
    subscription_pro_stars: int = Field(default=2250, validation_alias="SUBSCRIPTION_PRO_STARS")
    subscription_lite_usd_label: str = Field(default="10", validation_alias="SUBSCRIPTION_LITE_USD")
    subscription_pro_usd_label: str = Field(default="20", validation_alias="SUBSCRIPTION_PRO_USD")
    fx_fallback_usd_rub: float = Field(default=80.0, validation_alias="FX_FALLBACK_USD_RUB")
    fx_fallback_usd_byn: float = Field(default=3.0, validation_alias="FX_FALLBACK_USD_BYN")
    poll_interval_minutes: int = Field(default=15, validation_alias="POLL_INTERVAL_MINUTES")
    poller_stale_minutes: int = Field(default=35, validation_alias="POLLER_STALE_MINUTES")
    digest_hour_utc: int = Field(default=6, validation_alias="DIGEST_HOUR_UTC")
    stale_review_hours: int = Field(default=24, validation_alias="STALE_REVIEW_HOURS")
    stale_reminder_hour_utc: int = Field(default=15, validation_alias="STALE_REMINDER_HOUR_UTC")
    llm_queue_workers: int = Field(default=2, validation_alias="LLM_QUEUE_WORKERS")
    trial_pro_days: int = Field(default=3, validation_alias="TRIAL_PRO_DAYS")
    free_api_publishes: int = Field(default=3, validation_alias="FREE_API_PUBLISHES")
    support_username: str = Field(default="", validation_alias="SUPPORT_USERNAME")
    legal_operator_name: str = Field(
        default="",
        validation_alias="LEGAL_OPERATOR_NAME",
        description="Наименование оператора ПДн / исполнителя в юридических текстах бота",
    )
    product_news_version: str = Field(
        default="2025-10-v1",
        validation_alias="PRODUCT_NEWS_VERSION",
        description="Версия блока «Что нового» на сводке; смените строку — баннер снова покажется",
    )
    payment_activation_sla_hours: int = Field(
        default=24,
        validation_alias="PAYMENT_ACTIVATION_SLA_HOURS",
        description="SLA ручной активации подписки (QR / счёт), часы",
    )
    privacy_policy_url: str = Field(default="", validation_alias="PRIVACY_POLICY_URL")
    terms_of_service_url: str = Field(default="", validation_alias="TERMS_OF_SERVICE_URL")
    webhook_url: str = Field(default="", validation_alias="WEBHOOK_URL")
    webhook_path: str = Field(default="/webhook", validation_alias="WEBHOOK_PATH")
    webhook_host: str = Field(default="0.0.0.0", validation_alias="WEBHOOK_HOST")
    webhook_port: int = Field(default=8080, validation_alias="WEBHOOK_PORT")
    health_port: int = Field(default=8081, validation_alias="HEALTH_PORT")
    fsm_redis_url: str = Field(default="", validation_alias="FSM_REDIS_URL")
    sentry_dsn: str = Field(default="", validation_alias="SENTRY_DSN")
    qr_payment_instructions: str = Field(
        default=(
            "1. Перевод по QR / ERIP / на карту — реквизиты запросите в разделе «Поддержка».\n"
            "2. В комментарии к платежу укажите Telegram @username и тариф (Lite / PRO).\n"
            "3. Сохраните чек и нажмите «Я оплатил» в боте."
        ),
        validation_alias="QR_PAYMENT_INSTRUCTIONS",
    )
    legal_payment_instructions: str = Field(
        default=(
            "1. Напишите в поддержку: название организации, УНП/ИНН, тариф Lite или PRO, email для счёта.\n"
            "2. Мы выставим счёт на безналичную оплату (РФ / РБ).\n"
            "3. После поступления средств активируем подписку — обычно в течение рабочих суток."
        ),
        validation_alias="LEGAL_PAYMENT_INSTRUCTIONS",
    )

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: object) -> list[int]:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [int(item) for item in value]
        if isinstance(value, (int, float)):
            return [int(value)]
        if isinstance(value, str):
            parts = [part.strip() for part in value.split(",") if part.strip()]
            return [int(part) for part in parts]
        raise TypeError("ADMIN_IDS must be a comma-separated list of integers")


@lru_cache
def get_settings() -> Settings:
    return Settings()
