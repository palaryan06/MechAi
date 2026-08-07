"""Test MechAI custom exception hierarchy."""

from __future__ import annotations

import pytest

from mechai.common.exceptions import (
    CLIError,
    ConfigurationError,
    DocumentParseError,
    EmbeddingError,
    ExtractionError,
    GraphBuildError,
    IngestionError,
    LoggingError,
    MechAIError,
)


def test_exception_hierarchy() -> None:
    """Verify all custom exceptions inherit from MechAIError."""
    assert issubclass(ConfigurationError, MechAIError)
    assert issubclass(LoggingError, MechAIError)
    assert issubclass(CLIError, MechAIError)
    assert issubclass(IngestionError, MechAIError)
    assert issubclass(DocumentParseError, IngestionError)
    assert issubclass(ExtractionError, IngestionError)
    assert issubclass(GraphBuildError, IngestionError)
    assert issubclass(EmbeddingError, IngestionError)


def test_catch_by_base_class() -> None:
    """Verify exceptions can be caught by MechAIError base class."""
    with pytest.raises(MechAIError):
        raise ConfigurationError("Invalid database host")

    with pytest.raises(MechAIError):
        raise LoggingError("Failed to initialize logging handler")

    with pytest.raises(MechAIError):
        raise CLIError("Command failed")


def test_exception_message() -> None:
    """Verify exception messages are preserved."""
    err = ConfigurationError("Missing MECHAI_LOG_LEVEL")
    assert str(err) == "Missing MECHAI_LOG_LEVEL"
