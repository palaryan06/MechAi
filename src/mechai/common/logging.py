"""MechAI structured logging setup using structlog and standard library logging.

Call configure_logging() once at application startup. After that, obtain a logger with:

    from mechai.common.logging import get_logger
    logger = get_logger(__name__)
    logger.info("event_name", key="value", count=42)

Logs are emitted as JSON in production and as human-readable coloured output in development.
Reference: docs/engineering/04-logging-philosophy.md
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, Any

import structlog

from mechai.common.exceptions import LoggingError

if TYPE_CHECKING:
    from structlog.typing import FilteringBoundLogger


def configure_logging(
    *,
    level: str = "INFO",
    json_output: bool = False,
) -> None:
    """Configure structlog and standard library logging.

    Args:
        level: Log level string ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
        json_output: If True, emit JSON logs (production).
                     If False, emit human-readable coloured console logs (development).

    Raises:
        LoggingError: If configuring the logging system fails.
    """
    try:
        log_level = getattr(logging, level.upper(), logging.INFO)

        shared_processors: list[Any] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]

        if json_output:
            renderer: Any = structlog.processors.JSONRenderer()
        else:
            renderer = structlog.dev.ConsoleRenderer(colors=True)

        structlog.configure(
            processors=[
                *shared_processors,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=shared_processors,
        )

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

        root = logging.getLogger()
        root.handlers = [handler]
        root.setLevel(log_level)

        # Quiet noisy third-party loggers
        for noisy in ("httpx", "httpcore", "urllib3", "PIL", "torch", "asyncio"):
            logging.getLogger(noisy).setLevel(logging.WARNING)
    except Exception as exc:
        raise LoggingError(f"Failed to configure logging: {exc}") from exc


def get_logger(name: str | None = None) -> FilteringBoundLogger:
    """Obtain a structured logger instance.

    Args:
        name: Name for the logger (typically __name__).

    Returns:
        A structlog bound logger instance.
    """
    return structlog.get_logger(name)  # type: ignore[no-any-return]
