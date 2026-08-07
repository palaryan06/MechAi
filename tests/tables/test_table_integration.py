"""Integration and streaming parity tests for Automotive Table Intelligence Engine (RFC-AUTO-001).

Tests complete pipeline integration from PDF parsing to Layout Zoning, Reading Order,
and Table Intelligence reconstruction, verifying batch vs. streaming equivalence.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mechai.layout.factory import LayoutEngineFactory
from mechai.ordering.factory import ReadingOrderEngineFactory
from mechai.ingestion.parsing.factory import ParserFactory
from mechai.tables.engine import AutomotiveTableEngine
from mechai.tables.factory import AutomotiveTableEngineFactory

_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
_SAMPLE_PDF = _FIXTURES_DIR / "sample_manual.pdf"


@pytest.fixture(scope="module")
def sample_pdf_ordered_layout() -> tuple:
    """Fixture providing parsed, zoned, and ordered document representations."""
    parser = ParserFactory.create()
    parsed_doc = parser.parse(_SAMPLE_PDF)

    zoner = LayoutEngineFactory.create()
    layout_cir = zoner.process(parsed_doc)

    order_engine = ReadingOrderEngineFactory.create()
    ordered_cir = order_engine.order_layout(layout_cir)

    return parsed_doc, layout_cir, ordered_cir


class TestAutomotiveTableIntegration:
    """Test suite for end-to-end table reconstruction through the pipeline."""

    def test_sample_pdf_table_pipeline(self, sample_pdf_ordered_layout: tuple) -> None:
        _, _, ordered_cir = sample_pdf_ordered_layout
        table_engine = AutomotiveTableEngineFactory.create()

        table_set = table_engine.reconstruct_tables(ordered_cir)

        assert table_set.document_id == ordered_cir.document_id
        assert table_set.total_tables >= 1
        assert len(table_set.tables) == table_set.total_tables

        first_tbl = table_set.tables[0]
        assert first_tbl.page_number >= 1
        assert first_tbl.num_columns >= 2
        assert first_tbl.num_rows >= 1
        assert first_tbl.header.depth >= 1
        assert len(first_tbl.header.flat_column_names) == first_tbl.num_columns

        # Verify cell provenance and reading order reference
        for row in first_tbl.rows:
            for cell in row.cells:
                assert cell.page_number == first_tbl.page_number
                assert cell.reading_order_ref != ""
                assert cell.provenance.confidence > 0.0

    def test_streaming_and_batch_parity(self, sample_pdf_ordered_layout: tuple) -> None:
        """Verify that streaming page iterator produces identical tables as batch processing."""
        _, _, ordered_cir = sample_pdf_ordered_layout
        table_engine = AutomotiveTableEngine()

        # Batch
        batch_set = table_engine.reconstruct_tables(ordered_cir)

        # Stream
        streamed_tables = list(table_engine.reconstruct_stream(iter(ordered_cir.pages)))

        assert len(streamed_tables) == len(batch_set.tables)

        for b_tbl, s_tbl in zip(batch_set.tables, streamed_tables, strict=True):
            assert b_tbl.page_number == s_tbl.page_number
            assert b_tbl.num_columns == s_tbl.num_columns
            assert b_tbl.num_rows == s_tbl.num_rows
            assert b_tbl.header.flat_column_names == s_tbl.header.flat_column_names
            assert b_tbl.table_type == s_tbl.table_type
