from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    admin_ids: list[int] = Field(default_factory=list, validation_alias="ADMIN_IDS")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

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
