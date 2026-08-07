"""Document parsing subsystem for Stage 1 of the MechAI ingestion pipeline."""

from __future__ import annotations

from mechai.ingestion.parsing.base import DocumentParser
from mechai.ingestion.parsing.config import DocumentParserConfig, ParserBackend
from mechai.ingestion.parsing.docling_parser import DoclingParser
from mechai.ingestion.parsing.factory import ParserFactory
from mechai.ingestion.parsing.pymupdf_parser import PyMuPDFParser
from mechai.ingestion.parsing.result import ParserMetrics, ParserResult

__all__ = [
    "DoclingParser",
    "DocumentParser",
    "DocumentParserConfig",
    "ParserBackend",
    "ParserFactory",
    "ParserMetrics",
    "ParserResult",
    "PyMuPDFParser",
]
