"""Factory for creating document parser instances based on configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mechai.common.exceptions import ConfigurationError
from mechai.ingestion.parsing.config import DocumentParserConfig, ParserBackend
from mechai.ingestion.parsing.docling_parser import DoclingParser
from mechai.ingestion.parsing.pymupdf_parser import PyMuPDFParser

if TYPE_CHECKING:
    from mechai.ingestion.parsing.base import DocumentParser


class ParserFactory:
    """Factory for dependency-injected document parser creation."""

    _registry: ClassVar[dict[str, type[DocumentParser]]] = {
        ParserBackend.PYMUPDF: PyMuPDFParser,
        ParserBackend.DOCLING: DoclingParser,
    }

    @classmethod
    def register_backend(cls, name: str, parser_cls: type[DocumentParser]) -> None:
        """Register a custom parser backend implementation."""
        cls._registry[name.lower()] = parser_cls

    @classmethod
    def create(cls, config: DocumentParserConfig | None = None) -> DocumentParser:
        """Instantiate a DocumentParser backend configured according to DocumentParserConfig."""
        cfg = config or DocumentParserConfig()
        backend = cfg.backend

        if backend == ParserBackend.AUTO:
            # PyMuPDF is primary high-performance default for Stage 1 word & image extraction
            return PyMuPDFParser(config=cfg)

        parser_cls = cls._registry.get(backend.value)
        if parser_cls is None:
            available = list(cls._registry.keys())
            msg = f"Unknown parser backend: '{backend}'. Available backends: {available}"
            raise ConfigurationError(msg)

        return parser_cls(config=cfg)
