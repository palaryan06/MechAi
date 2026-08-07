"""Integration and streaming parity tests for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Tests complete pipeline integration from PDF parsing to Layout Zoning, Reading Order,
Automotive Table Intelligence, and Automotive Procedure reconstruction.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mechai.ingestion.parsing.factory import ParserFactory
from mechai.layout.factory import LayoutEngineFactory
from mechai.ordering.factory import ReadingOrderEngineFactory
from mechai.procedures.engine import AutomotiveProcedureEngine
from mechai.procedures.factory import AutomotiveProcedureEngineFactory
from mechai.tables.factory import AutomotiveTableEngineFactory

_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
_SAMPLE_PDF = _FIXTURES_DIR / "sample_manual.pdf"


@pytest.fixture(scope="module")
def sample_pdf_pipeline_data() -> tuple:
    """Fixture providing parsed, zoned, ordered CIR and reconstructed tables."""
    parser = ParserFactory.create()
    parsed_doc = parser.parse(_SAMPLE_PDF)

    zoner = LayoutEngineFactory.create()
    layout_cir = zoner.process(parsed_doc)

    order_engine = ReadingOrderEngineFactory.create()
    ordered_cir = order_engine.order_layout(layout_cir)

    table_engine = AutomotiveTableEngineFactory.create()
    table_set = table_engine.reconstruct_tables(ordered_cir)

    return parsed_doc, layout_cir, ordered_cir, table_set


class TestAutomotiveProcedureIntegration:
    """Test suite for end-to-end procedure reconstruction through the pipeline."""

    def test_sample_pdf_procedure_pipeline(self, sample_pdf_pipeline_data: tuple) -> None:
        _, _, ordered_cir, table_set = sample_pdf_pipeline_data
        engine = AutomotiveProcedureEngineFactory.create()

        procedure_set = engine.reconstruct_procedures(ordered_cir, table_set=table_set)

        assert procedure_set.document_id == ordered_cir.document_id
        assert procedure_set.total_procedures >= 1
        assert len(procedure_set.procedures) == procedure_set.total_procedures
        assert procedure_set.total_steps >= 1

        first_proc = procedure_set.procedures[0]
        assert first_proc.title != ""
        assert first_proc.page_span[0] >= 1
        assert first_proc.page_span[1] >= first_proc.page_span[0]
        assert len(first_proc.steps) >= 1

        # Verify step sequence monotonicity and spatial grounding
        for idx, step in enumerate(first_proc.steps, start=1):
            assert step.sequence_number == idx
            assert step.step_id != ""
            assert step.action_text != ""
            assert step.page_number >= first_proc.page_span[0]
            assert step.page_number <= first_proc.page_span[1]
            assert step.reading_order_ref != ""
            assert step.provenance.confidence > 0.0

    def test_streaming_and_batch_parity(self, sample_pdf_pipeline_data: tuple) -> None:
        """Verify that streaming page iterator reconstructs valid procedures matching batch processing."""
        _, _, ordered_cir, table_set = sample_pdf_pipeline_data
        engine = AutomotiveProcedureEngine()

        # Batch
        batch_set = engine.reconstruct_procedures(ordered_cir, table_set=table_set)

        # Stream
        streamed_procs = list(engine.reconstruct_stream(iter(ordered_cir.pages), table_set=table_set))

        # Stream produces page-by-page procedures before multi-page continuation stitching
        assert len(streamed_procs) >= len(batch_set.procedures)

        for s_proc in streamed_procs:
            assert s_proc.title != ""
            assert len(s_proc.steps) >= 1
            for step in s_proc.steps:
                assert step.action_text != ""
                assert step.sequence_number >= 1
