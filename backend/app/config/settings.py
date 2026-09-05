from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    APP_NAME: str = "Revora AI"
    APP_ENV: Literal["development", "test", "production"] = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./recovery.db"

    # Optional Redis dependency. The app can run without Redis in local/demo mode.
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI provider. `mock` keeps the project runnable without an API key.
    LLM_PROVIDER: Literal["mock", "openai"] = "mock"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

    # Frontend / API
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    API_PREFIX: str = "/api"

    # Recovery safety limits
    MAX_RECOVERY_ATTEMPTS: int = Field(default=3, ge=1, le=10)
    RECOVERY_CASE_TTL_HOURS: int = Field(default=72, ge=1, le=720)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def llm_enabled(self) -> bool:
        return self.LLM_PROVIDER != "mock" and bool(self.LLM_API_KEY)


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings object for the application process."""
    return Settings()


settings = get_settings()
