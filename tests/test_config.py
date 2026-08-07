"""Test MechAI configuration loading and validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mechai.common.config import (
    AppConfig,
    Environment,
    LogFormat,
    clear_config_cache,
    get_config,
)
from mechai.common.exceptions import ConfigurationError


def test_default_config() -> None:
    """Verify default configuration values."""
    config = AppConfig()
    assert config.app_name == "mechai"
    assert config.environment == Environment.DEVELOPMENT
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.log_format == LogFormat.CONSOLE
    assert config.is_development is True
    assert config.is_production is False
    assert config.is_testing is False


def test_env_var_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify environment variables with MECHAI_ prefix override defaults."""
    monkeypatch.setenv("MECHAI_APP_NAME", "custom-mechai")
    monkeypatch.setenv("MECHAI_ENV", "production")
    monkeypatch.setenv("MECHAI_DEBUG", "true")
    monkeypatch.setenv("MECHAI_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("MECHAI_LOG_FORMAT", "json")

    config = AppConfig()
    assert config.app_name == "custom-mechai"
    assert config.environment == Environment.PRODUCTION
    assert config.debug is True
    assert config.log_level == "DEBUG"
    assert config.log_format == LogFormat.JSON
    assert config.is_production is True
    assert config.is_development is False


def test_log_level_case_insensitivity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify log level is converted to uppercase."""
    monkeypatch.setenv("MECHAI_LOG_LEVEL", "warning")
    config = AppConfig()
    assert config.log_level == "WARNING"


def test_log_level_from_bytes() -> None:
    """Verify log level normalization accepts bytes."""
    normalized = AppConfig._normalize_log_level(b"debug")
    assert normalized == "DEBUG"


def test_invalid_log_level_type() -> None:
    """Verify invalid type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid log level type"):
        AppConfig._normalize_log_level(12345)


def test_invalid_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify invalid log level raises validation error."""
    monkeypatch.setenv("MECHAI_LOG_LEVEL", "INVALID_LEVEL")
    with pytest.raises(ValidationError):
        AppConfig()


def test_get_config_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify get_config caches the configuration singleton."""
    clear_config_cache()
    c1 = get_config()
    c2 = get_config()
    assert c1 is c2

    # Clearing cache returns a new instance
    monkeypatch.setenv("MECHAI_APP_NAME", "new-name")
    clear_config_cache()
    c3 = get_config()
    assert c3.app_name == "new-name"
    assert c3 is not c1


def test_get_config_wraps_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify get_config wraps validation errors in ConfigurationError."""
    clear_config_cache()
    monkeypatch.setenv("MECHAI_LOG_LEVEL", "NONEXISTENT")
    with pytest.raises(ConfigurationError):
        get_config()
