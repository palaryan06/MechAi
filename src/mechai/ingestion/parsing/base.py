"""Base interface for document parsing engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from mechai.contracts.scrubbing import ParsedDocument
    from mechai.ingestion.parsing.config import DocumentParserConfig
    from mechai.ingestion.parsing.result import ParserResult


class DocumentParser(ABC):
    """Abstract base class for all document parser backends."""

    def __init__(self, config: DocumentParserConfig | None = None) -> None:
        """Initialize document parser with optional configuration."""
        from mechai.ingestion.parsing.config import DocumentParserConfig

        self._config = config or DocumentParserConfig()

    @property
    def config(self) -> DocumentParserConfig:
        """Active configuration for this parser instance."""
        return self._config

    @abstractmethod
    def parse(self, source: str | Path | bytes) -> ParsedDocument:
        """Parse raw PDF file or bytes into a structured ParsedDocument."""
        ...

    @abstractmethod
    def parse_with_result(self, source: str | Path | bytes) -> ParserResult:
        """Parse raw PDF and return detailed ParserResult with metrics and metadata."""
        ...
