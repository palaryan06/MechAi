"""Integration tests connecting Stage 1 Parser, Stage 2.0 Layout, and Stage 2.1 Reading Order."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from mechai.contracts.ordering import FlowEdgeType, OrderedLayoutCIR
from mechai.ingestion.parsing import PyMuPDFParser
from mechai.layout import LayoutEngineFactory
from mechai.ordering import ReadingOrderEngineFactory

if TYPE_CHECKING:
    from mechai.contracts.layout import LayoutCIR

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_PDF = FIXTURES_DIR / "sample_manual.pdf"


class TestReadingOrderIntegration:
    """End-to-end integration across Stages 1.0, 2.0, and 2.1."""

    def test_sample_pdf_end_to_end_reading_order_pipeline(self) -> None:
        """Full pipeline: Raw PDF -> ParsedDocument -> LayoutCIR -> OrderedLayoutCIR."""
        assert SAMPLE_PDF.exists(), f"Sample PDF fixture missing at {SAMPLE_PDF}"

        # 1. Parse raw PDF (Stage 1.0)
        parser = PyMuPDFParser()
        parsed_doc = parser.parse(SAMPLE_PDF)
        assert parsed_doc.total_pages == 2

        # 2. Segment layout (Stage 2.0)
        layout_engine = LayoutEngineFactory.create()
        layout_cir: LayoutCIR = layout_engine.segment_layout(parsed_doc)
        assert len(layout_cir.pages) == 2

        # 3. Determine reading order & build graph (Stage 2.1)
        ordering_engine = ReadingOrderEngineFactory.create()
        ordered_cir: OrderedLayoutCIR = ordering_engine.order_layout(layout_cir)

        # 4. Verify Document-level structure
        assert isinstance(ordered_cir, OrderedLayoutCIR)
        assert ordered_cir.total_pages == 2
        assert len(ordered_cir.pages) == 2
        assert len(ordered_cir.ordered_regions) > 0

        # Verify global graph is valid DAG
        assert ordered_cir.global_graph.is_dag is True
        assert len(ordered_cir.global_graph.primary_path) > 0

        # 5. Verify Page 1 Reading Flow
        p1 = ordered_cir.pages[0]
        assert p1.page_number == 1
        assert len(p1.primary_sequence) > 0
        assert p1.reading_order_graph.is_dag is True
        assert p1.sequence_confidence > 0.80

        # Title should be first in primary sequence
        first_region = next(r for r in p1.ordered_regions if r.id == p1.primary_sequence[0])
        assert "MANUAL" in first_region.text or "SERVICE" in first_region.text

        # 6. Verify Page 2 Reading Flow (Figure, Caption, Steps, Table)
        p2 = ordered_cir.pages[1]
        assert p2.page_number == 2
        assert len(p2.primary_sequence) > 0
        assert p2.reading_order_graph.is_dag is True

        # Check if caption is linked to figure
        cap_edge = next(
            (e for e in p2.reading_order_graph.edges if e.edge_type == FlowEdgeType.CAPTION_LINK),
            None,
        )
        if cap_edge:
            assert "caption_binding" in cap_edge.evidence.decision_rule

        # 7. Verify Cross-Page Flow exists in Global Graph
        cross_edge = next(
            (
                e
                for e in ordered_cir.global_graph.edges
                if e.edge_type == FlowEdgeType.CROSS_PAGE_FLOW
            ),
            None,
        )
        assert cross_edge is not None
        assert cross_edge.evidence.decision_rule == "cross_page_continuation"
