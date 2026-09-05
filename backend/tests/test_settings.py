import os

from app.config.settings import Settings


def test_default_settings_are_safe_for_local_demo():
    settings = Settings()

    assert settings.APP_NAME == "Revora AI"
    assert settings.APP_ENV == "development"
    assert settings.LLM_PROVIDER == "mock"
    assert settings.llm_enabled is False
    assert settings.MAX_RECOVERY_ATTEMPTS == 3


def test_settings_accept_environment_overrides(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("MAX_RECOVERY_ATTEMPTS", "5")

    settings = Settings()

    assert settings.is_production is True
    assert settings.llm_enabled is True
    assert settings.MAX_RECOVERY_ATTEMPTS == 5


def test_invalid_recovery_attempt_limit_is_rejected():
    try:
        Settings(MAX_RECOVERY_ATTEMPTS=0)
    except Exception:
        return

    raise AssertionError("MAX_RECOVERY_ATTEMPTS=0 should be rejected")
