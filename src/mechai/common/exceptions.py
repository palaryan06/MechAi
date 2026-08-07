"""MechAI exception hierarchy.

Design rules:
- Every public exception inherits from MechAIError.
- Catch specific exceptions and reraise typed MechAI exceptions across layer boundaries.
- Never let third-party exceptions escape uncaught without context.
"""

from __future__ import annotations


class MechAIError(Exception):
    """Base exception for all MechAI errors."""


class ConfigurationError(MechAIError):
    """Raised for invalid or missing configuration values."""


class LoggingError(MechAIError):
    """Raised for logging initialization or configuration failures."""


class CLIError(MechAIError):
    """Raised when a CLI command or entry point fails."""


# ---------------------------------------------------------------------------
# Ingestion pipeline exceptions (reserved for ingestion subsystem)
# ---------------------------------------------------------------------------


class IngestionError(MechAIError):
    """Base class for all ingestion pipeline errors."""


class DocumentParseError(IngestionError):
    """Raised when document parsing fails."""


class ExtractionError(IngestionError):
    """Raised when structured content extraction fails."""


class GraphBuildError(IngestionError):
    """Raised when knowledge graph generation fails."""


class EmbeddingError(IngestionError):
    """Raised when embedding generation fails."""
