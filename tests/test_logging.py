"""Test MechAI structured logging setup."""

from __future__ import annotations

import logging

import pytest
import structlog

from mechai.common.exceptions import LoggingError
from mechai.common.logging import configure_logging, get_logger


def test_configure_logging_console() -> None:
    """Verify configure_logging initializes console logging successfully."""
    configure_logging(level="INFO", json_output=False)
    root = logging.getLogger()
    assert root.level == logging.INFO
    assert len(root.handlers) > 0


def test_configure_logging_json() -> None:
    """Verify configure_logging initializes JSON structured logging successfully."""
    configure_logging(level="DEBUG", json_output=True)
    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert len(root.handlers) > 0


def test_get_logger() -> None:
    """Verify get_logger returns a functional bound logger."""
    logger = get_logger("test.module")
    assert logger is not None
    # Verify logger can emit events without crashing
    logger.info("test_event", key="value", numeric_id=123)


def test_log_level_filtering() -> None:
    """Verify setting higher log level is reflected in root logger."""
    configure_logging(level="ERROR", json_output=False)
    root = logging.getLogger()
    assert root.level == logging.ERROR


def test_configure_logging_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify LoggingError is raised when configuration fails."""

    def broken_configure(*args: object, **kwargs: object) -> None:
        raise RuntimeError("Structlog initialization failure")

    monkeypatch.setattr(structlog, "configure", broken_configure)
    with pytest.raises(LoggingError):
        configure_logging()
