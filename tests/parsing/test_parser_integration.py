"""Integration tests for the Document Parsing Engine on synthetic workshop manuals."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from mechai.contracts.scrubbing import ParsedDocument
from mechai.ingestion.parsing import DocumentParserConfig, ParserFactory, PyMuPDFParser

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_PDF = FIXTURES_DIR / "sample_manual.pdf"


class TestParserIntegration:
    """Integration test suite executing end-to-end PDF parsing."""

    def test_parse_from_path(self) -> None:
        parser = PyMuPDFParser()
        result = parser.parse_with_result(SAMPLE_PDF)

        # Verify result wrapper and metrics
        assert result.metrics.page_count == 2
        assert result.metrics.word_count > 100
        assert result.metrics.image_count == 1
        assert result.metrics.backend == "pymupdf"
        assert result.metrics.elapsed_ms >= 0.0

        # Verify metadata
        assert result.metadata.get("title") == "Sample Automotive Workshop Manual"
        assert result.metadata.get("author") == "MechAI Engineering"
        assert result.metadata.get("subject") == "Cooling System Service & Diagnostic Procedures"

        # Verify document content
        doc = result.document
        assert doc.total_pages == 2
        assert doc.source_path is not None
        assert "sample_manual.pdf" in doc.source_path

        # Page 1 checks
        page1 = doc.pages[0]
        assert page1.page_number == 1
        assert page1.width == pytest.approx(612.0)
        assert page1.height == pytest.approx(792.0)
        assert "MECHAI AUTOMOTIVE SERVICE MANUAL" in page1.text
        assert "Cooling System" in page1.text
        assert len(page1.words) > 30

        # Check word bounding boxes and attributes
        first_word = page1.words[0]
        assert first_word.text == "MECHAI"
        assert first_word.left < first_word.right
        assert first_word.top < first_word.bottom
        assert first_word.font_size == pytest.approx(18.0)

        # Page 2 checks (Procedures, image, table)
        page2 = doc.pages[1]
        assert page2.page_number == 2
        assert len(page2.images) == 1

        img = page2.images[0]
        assert img.image_id.startswith("img_p2_")
        assert img.width == 120
        assert img.height == 80
        assert img.bbox is not None
        assert img.bbox.left < img.bbox.right
        assert img.bbox.top < img.bbox.bottom

        # Verify table text presence
        assert "Thermostat Opening Valve" in page2.text
        assert "82 C" in page2.text

    def test_parse_from_bytes(self) -> None:
        pdf_bytes = SAMPLE_PDF.read_bytes()
        parser = ParserFactory.create()
        doc = parser.parse(pdf_bytes)

        assert isinstance(doc, ParsedDocument)
        assert doc.total_pages == 2
        assert doc.source_path is None

    def test_parse_with_image_extraction_to_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "extracted_images"
            config = DocumentParserConfig(image_output_dir=out_dir)
            parser = PyMuPDFParser(config=config)

            result = parser.parse_with_result(SAMPLE_PDF)
            page2 = result.document.pages[1]
            assert len(page2.images) == 1

            saved_image = page2.images[0]
            assert saved_image.file_path is not None
            saved_path = Path(saved_image.file_path)
            assert saved_path.exists()
            assert saved_path.stat().st_size > 0
            assert saved_path.suffix == ".png"

    def test_parse_with_max_pages_limit(self) -> None:
        config = DocumentParserConfig(max_pages=1)
        parser = PyMuPDFParser(config=config)
        doc = parser.parse(SAMPLE_PDF)

        assert doc.total_pages == 1
        assert doc.pages[0].page_number == 1
