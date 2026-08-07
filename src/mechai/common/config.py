"""MechAI configuration management.

Centralized configuration loaded from environment variables (with a MECHAI_ prefix)
and optional .env files.

Reference: docs/engineering/06-configuration-philosophy.md
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from mechai.common.exceptions import ConfigurationError


class Environment(StrEnum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogFormat(StrEnum):
    """Supported log output formats."""

    CONSOLE = "console"
    JSON = "json"


class AppConfig(BaseSettings):
    """Core application configuration for MechAI.

    All properties can be populated or overridden via environment variables
    with the 'MECHAI_' prefix (e.g., MECHAI_LOG_LEVEL=DEBUG).
    """

    model_config = SettingsConfigDict(
        env_prefix="MECHAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(
        default="mechai",
        description="Application identifier name.",
    )
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        validation_alias=AliasChoices(
            "mechai_environment",
            "mechai_env",
            "environment",
            "env",
        ),
        description="Deployment environment (development, staging, production, testing).",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode with verbose diagnostic output.",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level threshold.",
    )
    log_format: LogFormat = Field(
        default=LogFormat.CONSOLE,
        validation_alias=AliasChoices(
            "mechai_log_format",
            "mechai_format",
            "log_format",
            "format",
        ),
        description="Log output format: console (human-readable) or json (structured).",
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalize_log_level(cls, v: object) -> str:
        """Normalize log level string to uppercase."""
        if isinstance(v, str):
            upper_v = v.upper()
            valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
            if upper_v not in valid_levels:
                raise ValueError(f"Invalid log level: {v!r}. Must be one of {sorted(valid_levels)}")
            return upper_v
        if isinstance(v, bytes):
            return cls._normalize_log_level(v.decode("utf-8"))
        raise ValueError(f"Invalid log level type: {type(v).__name__}")

    @property
    def is_production(self) -> bool:
        """Return True if running in production environment."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Return True if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Return True if running in testing environment."""
        return self.environment == Environment.TESTING


# Alias for backward compatibility
Settings = AppConfig


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Return a cached singleton instance of AppConfig.

    Raises:
        ConfigurationError: If configuration values fail validation.
    """
    try:
        return AppConfig()
    except Exception as exc:
        raise ConfigurationError(f"Failed to load application configuration: {exc}") from exc


def clear_config_cache() -> None:
    """Clear the cached configuration singleton (useful for tests)."""
    get_config.cache_clear()
