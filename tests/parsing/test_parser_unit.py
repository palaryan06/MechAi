"""Unit tests for the Document Parsing Engine (Stage 1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from mechai.common.exceptions import ConfigurationError, DocumentParseError
from mechai.contracts.scrubbing import ParsedDocument
from mechai.contracts.stages import PdfParserProtocol
from mechai.ingestion.parsing import (
    DocumentParser,
    DocumentParserConfig,
    ParserBackend,
    ParserFactory,
    ParserResult,
    PyMuPDFParser,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_PDF = FIXTURES_DIR / "sample_manual.pdf"


class TestDocumentParserConfig:
    """Test configuration validation and immutability."""

    def test_default_config(self) -> None:
        config = DocumentParserConfig()
        assert config.backend == ParserBackend.AUTO
        assert config.extract_images is True
        assert config.extract_words is True
        assert config.image_output_dir is None
        assert config.max_pages is None
        assert config.start_page == 1
        assert config.min_word_length == 1
        assert config.dpi == 150
        assert config.timeout_seconds == 300.0

    def test_custom_config(self) -> None:
        out_dir = Path("/tmp/images")
        config = DocumentParserConfig(
            backend=ParserBackend.PYMUPDF,
            extract_images=False,
            extract_words=True,
            image_output_dir=out_dir,
            max_pages=5,
            start_page=2,
            min_word_length=3,
            dpi=300,
            timeout_seconds=60.0,
        )
        assert config.backend == ParserBackend.PYMUPDF
        assert config.extract_images is False
        assert config.max_pages == 5
        assert config.start_page == 2
        assert config.min_word_length == 3
        assert config.dpi == 300

    def test_config_immutability(self) -> None:
        config = DocumentParserConfig()
        with pytest.raises(ValidationError):
            setattr(config, "extract_images", False)

    def test_invalid_start_page(self) -> None:
        with pytest.raises(ValidationError):
            DocumentParserConfig(start_page=0)

    def test_invalid_dpi_bounds(self) -> None:
        with pytest.raises(ValidationError):
            DocumentParserConfig(dpi=50)  # Below 72
        with pytest.raises(ValidationError):
            DocumentParserConfig(dpi=1000)  # Above 600

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            DocumentParserConfig(**{"unknown_field": 123})  # type: ignore[arg-type]


class TestParserFactory:
    """Test factory creation and backend registration."""

    def test_create_auto_defaults_to_pymupdf(self) -> None:
        parser = ParserFactory.create(DocumentParserConfig(backend=ParserBackend.AUTO))
        assert isinstance(parser, PyMuPDFParser)
        assert isinstance(parser, PdfParserProtocol)

    def test_create_pymupdf_explicitly(self) -> None:
        parser = ParserFactory.create(DocumentParserConfig(backend=ParserBackend.PYMUPDF))
        assert isinstance(parser, PyMuPDFParser)

    def test_create_docling_when_missing_raises(self) -> None:
        # Since docling is not in the active python env, instantiating raises DocumentParseError
        with pytest.raises(DocumentParseError, match="Docling backend requires 'docling'"):
            ParserFactory.create(DocumentParserConfig(backend=ParserBackend.DOCLING))

    def test_custom_backend_registration(self) -> None:
        class DummyParser(DocumentParser):
            def parse(self, source: str | Path | bytes) -> ParsedDocument:
                return ParsedDocument()

            def parse_with_result(self, source: str | Path | bytes) -> ParserResult:
                raise NotImplementedError

        ParserFactory.register_backend("dummy", DummyParser)
        custom_p = DummyParser()
        assert isinstance(custom_p.parse(b"dummy"), ParsedDocument)

    def test_create_with_none_config(self) -> None:
        parser = ParserFactory.create(None)
        assert isinstance(parser, PyMuPDFParser)
        assert parser.config.backend == ParserBackend.AUTO

    def test_unregistered_backend_lookup_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Mock registry missing an enum value to test error branch
        monkeypatch.setattr(ParserFactory, "_registry", {})
        with pytest.raises(ConfigurationError, match="Unknown parser backend"):
            ParserFactory.create(DocumentParserConfig(backend=ParserBackend.PYMUPDF))

    def test_unknown_backend_raises(self) -> None:
        with pytest.raises(ValidationError):
            # ParserBackend enum prevents arbitrary strings via Pydantic
            DocumentParserConfig(backend="nonexistent")  # type: ignore[arg-type]


class TestPyMuPDFParserErrors:
    """Test error handling and edge cases in PyMuPDFParser."""

    def test_nonexistent_file_raises(self) -> None:
        parser = PyMuPDFParser()
        with pytest.raises(DocumentParseError, match="does not exist"):
            parser.parse(Path("tests/fixtures/does_not_exist_12345.pdf"))

    def test_empty_bytes_raises(self) -> None:
        parser = PyMuPDFParser()
        with pytest.raises(DocumentParseError, match="byte buffer is empty"):
            parser.parse(b"")

    def test_corrupt_bytes_raises(self) -> None:
        parser = PyMuPDFParser()
        with pytest.raises(DocumentParseError, match="Corrupt or invalid PDF data"):
            parser.parse(b"not a valid pdf header content")

    def test_start_page_out_of_bounds(self) -> None:
        parser = PyMuPDFParser(DocumentParserConfig(start_page=999))
        with pytest.raises(DocumentParseError, match="exceeds total pages"):
            parser.parse(SAMPLE_PDF)
