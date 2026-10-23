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
    payment_currency: str = Field(default="RUB", validation_alias="PAYMENT_CURRENCY")
    subscription_lite_price_minor: int = Field(
        default=100000,
        validation_alias="SUBSCRIPTION_LITE_PRICE_MINOR",
    )
    subscription_pro_price_minor: int = Field(
        default=300000,
        validation_alias="SUBSCRIPTION_PRO_PRICE_MINOR",
    )
    subscription_lite_stars: int = Field(default=750, validation_alias="SUBSCRIPTION_LITE_STARS")
    subscription_pro_stars: int = Field(default=2250, validation_alias="SUBSCRIPTION_PRO_STARS")
    subscription_lite_usd_label: str = Field(default="10", validation_alias="SUBSCRIPTION_LITE_USD")
    subscription_pro_usd_label: str = Field(default="30", validation_alias="SUBSCRIPTION_PRO_USD")
    poll_interval_minutes: int = Field(default=15, validation_alias="POLL_INTERVAL_MINUTES")
    trial_pro_days: int = Field(default=7, validation_alias="TRIAL_PRO_DAYS")
    free_api_publishes: int = Field(default=3, validation_alias="FREE_API_PUBLISHES")
    support_username: str = Field(default="", validation_alias="SUPPORT_USERNAME")
    webhook_url: str = Field(default="", validation_alias="WEBHOOK_URL")
    webhook_path: str = Field(default="/webhook", validation_alias="WEBHOOK_PATH")
    webhook_host: str = Field(default="0.0.0.0", validation_alias="WEBHOOK_HOST")
    webhook_port: int = Field(default=8080, validation_alias="WEBHOOK_PORT")
    health_port: int = Field(default=8081, validation_alias="HEALTH_PORT")
    sentry_dsn: str = Field(default="", validation_alias="SENTRY_DSN")
    qr_payment_instructions: str = Field(
        default=(
            "1. Отсканируйте QR-код вашего банка (ERIP / перевод по номеру телефона — реквизиты уточняйте у поддержки).\n"
            "2. В комментарии укажите ваш Telegram @username или ID.\n"
            "3. Сохраните чек об оплате."
        ),
        validation_alias="QR_PAYMENT_INSTRUCTIONS",
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
