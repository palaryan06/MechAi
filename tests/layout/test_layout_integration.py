"""Integration tests for Stage 2.0 Layout Intelligence Engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from mechai.contracts.layout import LayoutCIR, RegionType
from mechai.ingestion.parsing import PyMuPDFParser
from mechai.layout import LayoutEngineFactory

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_PDF = FIXTURES_DIR / "sample_manual.pdf"


class TestLayoutIntegration:
    """Integration test suite connecting Stage 1 Parser with Stage 2.0 Layout Engine."""

    def test_sample_pdf_end_to_end_layout_segmentation(self) -> None:
        assert SAMPLE_PDF.exists(), f"Sample PDF fixture missing at {SAMPLE_PDF}"

        # 1. Parse raw PDF using PyMuPDFParser
        parser = PyMuPDFParser()
        parsed_doc = parser.parse(SAMPLE_PDF)
        assert parsed_doc.total_pages == 2

        # 2. Execute Stage 2.0 Layout Intelligence Engine
        layout_engine = LayoutEngineFactory.create()
        layout_cir: LayoutCIR = layout_engine.segment_layout(parsed_doc)

        # 3. Assert document-level CIR structure
        assert isinstance(layout_cir, LayoutCIR)
        assert layout_cir.total_pages == 2
        assert len(layout_cir.pages) == 2
        assert len(layout_cir.regions) > 0
        assert layout_cir.provenance.confidence == 1.0

        # 4. Verify Page 1 layout elements (Title, Section Header, Paragraph, Warning, Spec)
        page1 = layout_cir.pages[0]
        assert page1.page_number == 1
        assert page1.width == pytest.approx(612.0)
        assert page1.height == pytest.approx(792.0)

        p1_types = {r.region_type for r in page1.regions}
        assert RegionType.TITLE in p1_types or RegionType.HEADING in p1_types
        assert RegionType.WARNING_BOX in p1_types
        assert RegionType.PARAGRAPH in p1_types

        # Verify Warning Box region on page 1
        warning_regions = [r for r in page1.regions if r.region_type == RegionType.WARNING_BOX]
        assert len(warning_regions) >= 1
        assert "WARNING:" in warning_regions[0].text
        assert warning_regions[0].confidence >= 0.90

        # 5. Verify Page 2 layout elements (Procedure list, Figure, Caption, Table)
        page2 = layout_cir.pages[1]
        assert page2.page_number == 2

        p2_types = {r.region_type for r in page2.regions}
        assert RegionType.FIGURE_REGION in p2_types
        assert RegionType.CAPTION in p2_types
        assert RegionType.LIST in p2_types or RegionType.PARAGRAPH in p2_types
        assert RegionType.TABLE_REGION in p2_types

        # Verify Figure Region on page 2
        fig_regions = [r for r in page2.regions if r.region_type == RegionType.FIGURE_REGION]
        assert len(fig_regions) >= 1
        assert fig_regions[0].bbox.width > 0.0

        # Verify Caption Region on page 2
        caption_regions = [r for r in page2.regions if r.region_type == RegionType.CAPTION]
        assert len(caption_regions) >= 1
        assert "Figure 11-1" in caption_regions[0].text
