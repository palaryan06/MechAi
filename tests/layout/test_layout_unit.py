"""Unit tests for Stage 2.0 Layout Intelligence Engine."""

from __future__ import annotations

import pytest

from mechai.contracts.layout import (
    ColumnGutter,
    GeometricLayoutZonerProtocol,
    LayoutCIR,
    LayoutEngineProtocol,
    LayoutRegion,
    PageLayoutCIR,
    PageMargins,
    RegionType,
)
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.contracts.scrubbing import (
    ParsedDocument,
    ParsedImage,
    ParsedPage,
    ParsedWord,
)
from mechai.layout import GeometricLayoutZoner, LayoutEngineFactory, LayoutZonerConfig


def _make_word(
    text: str,
    left: float,
    top: float,
    right: float,
    bottom: float,
    font_size: float = 10.0,
    font_name: str = "Helvetica",
    bold: bool = False,
    italic: bool = False,
) -> ParsedWord:
    return ParsedWord(
        text=text,
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        font_size=font_size,
        font_name=font_name,
        bold=bold,
        italic=italic,
    )


class TestLayoutContracts:
    """Validate Layout CIR contracts, enums, models, and constraints."""

    def test_all_16_region_types_exist(self) -> None:
        """Verify all 16 RFC-007 region types are represented in RegionType enum."""
        expected_types = {
            "Header",
            "Footer",
            "Margin",
            "Title",
            "Heading",
            "Subheading",
            "Paragraph",
            "List",
            "TableRegion",
            "FigureRegion",
            "Caption",
            "Body",
            "WarningBox",
            "NoteBox",
            "Sidebar",
            "Unknown",
        }
        actual_types = {rt.value for rt in RegionType}
        assert expected_types == actual_types

    def test_layout_region_immutability(self) -> None:
        """Verify LayoutRegion is frozen and immutable with extra='forbid'."""
        from pydantic import ValidationError

        bbox = BoundingBox(left=50.0, top=50.0, right=200.0, bottom=100.0)
        provenance = SourceRef(
            page_number=1,
            extraction_method=ExtractionMethod.RULE,
            confidence=0.95,
            bbox=bbox,
        )
        region = LayoutRegion(
            id="reg_p1_001",
            bbox=bbox,
            page_number=1,
            region_type=RegionType.PARAGRAPH,
            confidence=0.95,
            provenance=provenance,
            text="Sample paragraph",
        )
        with pytest.raises(ValidationError):
            setattr(region, "confidence", 0.5)

    def test_page_margins_and_column_gutter(self) -> None:
        """Verify PageMargins and ColumnGutter structure and immutability."""
        margins = PageMargins(left=54.0, top=54.0, right=54.0, bottom=54.0)
        assert margins.left == 54.0

        gutter = ColumnGutter(left=290.0, right=310.0, top=54.0, bottom=738.0)
        assert gutter.width == 20.0
        assert gutter.height == 684.0


class TestGeometricZoning:
    """Validate geometric zoning, margin estimation, and column detection algorithms."""

    def test_empty_page_returns_default_margins_and_no_regions(self) -> None:
        """Empty page should yield standard default margins and empty regions tuple."""
        zoner = GeometricLayoutZoner()
        empty_page = ParsedPage(page_number=1, width=612.0, height=792.0)
        layout = zoner.segment_page(empty_page)

        assert layout.page_number == 1
        assert layout.width == 612.0
        assert layout.height == 792.0
        assert layout.margins.left == 36.0
        assert layout.header_zone is None
        assert layout.footer_zone is None
        assert len(layout.regions) == 0

    def test_header_and_footer_detection(self) -> None:
        """Verify tokens in the top 10% and bottom 10% are zoned as Header and Footer."""
        zoner = GeometricLayoutZoner()
        words = (
            _make_word("SECTION 1A - GENERAL", 50.0, 20.0, 200.0, 32.0, font_size=8.0),
            _make_word("Page 1", 520.0, 20.0, 560.0, 32.0, font_size=8.0),
            _make_word("Sample", 50.0, 200.0, 100.0, 212.0, font_size=10.0),
            _make_word("paragraph", 105.0, 200.0, 160.0, 212.0, font_size=10.0),
            _make_word("content", 165.0, 200.0, 210.0, 212.0, font_size=10.0),
            _make_word(
                "CONFIDENTIAL - SUZUKI MOTOR CORP",
                180.0,
                760.0,
                420.0,
                772.0,
                font_size=8.0,
            ),
        )
        page = ParsedPage(page_number=1, width=612.0, height=792.0, words=words)
        layout = zoner.segment_page(page)

        types = [r.region_type for r in layout.regions]
        assert RegionType.HEADER in types
        assert RegionType.FOOTER in types
        assert RegionType.PARAGRAPH in types

        header_reg = next(r for r in layout.regions if r.region_type == RegionType.HEADER)
        assert "SECTION 1A" in header_reg.text

        footer_reg = next(r for r in layout.regions if r.region_type == RegionType.FOOTER)
        assert "CONFIDENTIAL" in footer_reg.text

    def test_multi_column_detection_two_columns(self) -> None:
        """Verify vertical projection histogram slices dual-column layouts."""
        zoner = GeometricLayoutZoner()
        col1_words = [
            _make_word(
                f"L{i}",
                50.0,
                100.0 + i * 15.0,
                240.0,
                112.0 + i * 15.0,
                font_size=10.0,
            )
            for i in range(10)
        ]
        col2_words = [
            _make_word(
                f"R{i}",
                340.0,
                100.0 + i * 15.0,
                550.0,
                112.0 + i * 15.0,
                font_size=10.0,
            )
            for i in range(10)
        ]
        page = ParsedPage(
            page_number=1,
            width=612.0,
            height=792.0,
            words=tuple(col1_words + col2_words),
        )
        layout = zoner.segment_page(page)

        assert len(layout.columns) == 1
        gutter = layout.columns[0]
        assert gutter.left >= 235.0
        assert gutter.right <= 345.0

    def test_multi_column_detection_three_columns(self) -> None:
        """Verify vertical projection histogram slices three-column layouts."""
        zoner = GeometricLayoutZoner()
        col1 = [
            _make_word(f"C1_{i}", 50.0, 100.0 + i * 15.0, 120.0, 112.0 + i * 15.0) for i in range(8)
        ]
        col2 = [
            _make_word(f"C2_{i}", 200.0, 100.0 + i * 15.0, 270.0, 112.0 + i * 15.0)
            for i in range(8)
        ]
        col3 = [
            _make_word(f"C3_{i}", 350.0, 100.0 + i * 15.0, 420.0, 112.0 + i * 15.0)
            for i in range(8)
        ]

        page = ParsedPage(
            page_number=1,
            width=612.0,
            height=792.0,
            words=tuple(col1 + col2 + col3),
        )
        layout = zoner.segment_page(page)

        assert len(layout.columns) == 2


class TestRegionClassification:
    """Validate typographic classification across region types."""

    def test_title_classification(self) -> None:
        """Title should be detected from large bold typography."""
        zoner = GeometricLayoutZoner()
        words = (
            _make_word(
                "ENGINE OVERHAUL MANUAL",
                50.0,
                100.0,
                350.0,
                125.0,
                font_size=18.0,
                bold=True,
            ),
            _make_word("This is body text.", 50.0, 140.0, 200.0, 152.0, font_size=10.0),
        )
        page = ParsedPage(page_number=1, width=612.0, height=792.0, words=words)
        layout = zoner.segment_page(page)

        title_regs = [r for r in layout.regions if r.region_type == RegionType.TITLE]
        assert len(title_regs) == 1
        assert title_regs[0].text == "ENGINE OVERHAUL MANUAL"
        assert title_regs[0].confidence >= 0.90

    def test_heading_and_subheading_classification(self) -> None:
        """Intermediate font sizes should classify as Heading/Subheading."""
        zoner = GeometricLayoutZoner()
        words = (
            _make_word(
                "Section 11: Cooling System",
                50.0,
                80.0,
                250.0,
                96.0,
                font_size=14.0,
                bold=True,
            ),
            _make_word(
                "Thermostat Inspection",
                50.0,
                120.0,
                200.0,
                133.0,
                font_size=11.5,
                bold=True,
            ),
            _make_word(
                "Check valve opening temperature.",
                50.0,
                150.0,
                250.0,
                162.0,
                font_size=10.0,
            ),
        )
        page = ParsedPage(page_number=1, width=612.0, height=792.0, words=words)
        layout = zoner.segment_page(page)

        types = [r.region_type for r in layout.regions]
        assert RegionType.HEADING in types or RegionType.TITLE in types

    def test_warning_box_classification(self) -> None:
        """Warning / Caution start tokens classify as WarningBox."""
        zoner = GeometricLayoutZoner()
        words = (
            _make_word("WARNING:", 50.0, 100.0, 110.0, 113.0, font_size=11.0, bold=True),
            _make_word("Do", 115.0, 100.0, 130.0, 113.0, font_size=10.0),
            _make_word("not", 135.0, 100.0, 155.0, 113.0, font_size=10.0),
            _make_word("open", 160.0, 100.0, 185.0, 113.0, font_size=10.0),
            _make_word("when", 190.0, 100.0, 220.0, 113.0, font_size=10.0),
            _make_word("hot.", 225.0, 100.0, 250.0, 113.0, font_size=10.0),
        )
        page = ParsedPage(page_number=1, width=612.0, height=792.0, words=words)
        layout = zoner.segment_page(page)

        warn_regs = [r for r in layout.regions if r.region_type == RegionType.WARNING_BOX]
        assert len(warn_regs) == 1
        assert "WARNING:" in warn_regs[0].text
        assert warn_regs[0].confidence >= 0.90

    def test_note_box_classification(self) -> None:
        """Note / Important start tokens classify as NoteBox."""
        zoner = GeometricLayoutZoner()
        words = (
            _make_word("NOTE:", 50.0, 100.0, 90.0, 113.0, font_size=10.0, bold=True),
            _make_word("Apply", 95.0, 100.0, 130.0, 113.0, font_size=10.0),
            _make_word("clean", 135.0, 100.0, 165.0, 113.0, font_size=10.0),
            _make_word("engine", 170.0, 100.0, 210.0, 113.0, font_size=10.0),
            _make_word("oil.", 215.0, 100.0, 240.0, 113.0, font_size=10.0),
        )
        page = ParsedPage(page_number=1, width=612.0, height=792.0, words=words)
        layout = zoner.segment_page(page)

        note_regs = [r for r in layout.regions if r.region_type == RegionType.NOTE_BOX]
        assert len(note_regs) == 1
        assert "NOTE:" in note_regs[0].text
        assert note_regs[0].confidence >= 0.90

    def test_list_classification(self) -> None:
        """Numbered and bulleted items classify as List."""
        zoner = GeometricLayoutZoner()
        words = (
            _make_word("1.", 50.0, 100.0, 60.0, 112.0, font_size=10.0),
            _make_word("Remove", 65.0, 100.0, 110.0, 112.0, font_size=10.0),
            _make_word("bolts.", 115.0, 100.0, 150.0, 112.0, font_size=10.0),
            _make_word("2.", 50.0, 120.0, 60.0, 132.0, font_size=10.0),
            _make_word("Detach", 65.0, 120.0, 105.0, 132.0, font_size=10.0),
            _make_word("cover.", 110.0, 120.0, 145.0, 132.0, font_size=10.0),
        )
        page = ParsedPage(page_number=1, width=612.0, height=792.0, words=words)
        layout = zoner.segment_page(page)

        list_regs = [r for r in layout.regions if r.region_type == RegionType.LIST]
        assert len(list_regs) == 1
        assert "1. Remove bolts." in list_regs[0].text
        assert list_regs[0].confidence >= 0.90

    def test_figure_region_and_caption_classification(self) -> None:
        """ParsedImage converts to FigureRegion and adjacent figure text to Caption."""
        zoner = GeometricLayoutZoner()
        image = ParsedImage(
            image_id="img_001",
            bbox=BoundingBox(left=50.0, top=100.0, right=250.0, bottom=250.0),
            width=200,
            height=150,
            image_format="png",
        )
        caption_words = (
            _make_word("Figure", 50.0, 260.0, 90.0, 272.0, font_size=9.0, bold=True),
            _make_word("1-1:", 95.0, 260.0, 120.0, 272.0, font_size=9.0, bold=True),
            _make_word("Thermostat", 125.0, 260.0, 180.0, 272.0, font_size=9.0),
            _make_word("Assembly", 185.0, 260.0, 240.0, 272.0, font_size=9.0),
        )
        page = ParsedPage(
            page_number=1,
            width=612.0,
            height=792.0,
            words=caption_words,
            images=(image,),
        )
        layout = zoner.segment_page(page)

        fig_regs = [r for r in layout.regions if r.region_type == RegionType.FIGURE_REGION]
        assert len(fig_regs) == 1
        assert fig_regs[0].bbox.left == 50.0

        cap_regs = [r for r in layout.regions if r.region_type == RegionType.CAPTION]
        assert len(cap_regs) == 1
        assert "Figure 1-1:" in cap_regs[0].text

    def test_table_region_classification(self) -> None:
        """Grid delimiter lines classify as TableRegion."""
        zoner = GeometricLayoutZoner()
        words = (
            _make_word("Item", 50.0, 100.0, 80.0, 112.0, font_size=10.0),
            _make_word("Specification", 200.0, 100.0, 280.0, 112.0, font_size=10.0),
            _make_word("Limit", 400.0, 100.0, 440.0, 112.0, font_size=10.0),
            _make_word("Thermostat", 50.0, 120.0, 110.0, 132.0, font_size=10.0),
            _make_word("82 C", 200.0, 120.0, 230.0, 132.0, font_size=10.0),
            _make_word("80 - 84 C", 400.0, 120.0, 460.0, 132.0, font_size=10.0),
        )
        page = ParsedPage(page_number=1, width=612.0, height=792.0, words=words)
        layout = zoner.segment_page(page)

        table_regs = [r for r in layout.regions if r.region_type == RegionType.TABLE_REGION]
        assert len(table_regs) == 1
        assert table_regs[0].confidence >= 0.85


class TestFactoryAndDependencyInjection:
    """Validate Factory and DI registration patterns."""

    def test_factory_creates_protocol_instance(self) -> None:
        """Factory.create() should instantiate an object fulfilling both protocols."""
        zoner = LayoutEngineFactory.create()
        assert isinstance(zoner, GeometricLayoutZonerProtocol)
        assert isinstance(zoner, LayoutEngineProtocol)

    def test_factory_with_custom_config(self) -> None:
        """Factory accepts custom config overrides."""
        cfg = LayoutZonerConfig(
            min_margin_pt=40.0,
            header_max_y_ratio=0.12,
            footer_min_y_ratio=0.88,
        )
        zoner = LayoutEngineFactory.create(config=cfg)
        assert isinstance(zoner, GeometricLayoutZoner)
        assert zoner.config.min_margin_pt == 40.0
        assert zoner.config.header_max_y_ratio == 0.12


class TestStreamingParity:
    """Verify batch and streaming methods produce identical CIR outputs."""

    def test_streaming_and_batch_equivalence(self) -> None:
        """process() and process_stream() must return matching PageLayoutCIR objects."""
        zoner = GeometricLayoutZoner()
        page1 = ParsedPage(
            page_number=1,
            width=612.0,
            height=792.0,
            words=(
                _make_word(
                    "Service Manual Page 1",
                    50.0,
                    20.0,
                    200.0,
                    32.0,
                    font_size=8.0,
                ),
                _make_word(
                    "Chapter 1 Overview",
                    50.0,
                    100.0,
                    250.0,
                    120.0,
                    font_size=16.0,
                    bold=True,
                ),
            ),
        )
        page2 = ParsedPage(
            page_number=2,
            width=612.0,
            height=792.0,
            words=(
                _make_word(
                    "Service Manual Page 2",
                    50.0,
                    20.0,
                    200.0,
                    32.0,
                    font_size=8.0,
                ),
                _make_word(
                    "Chapter 2 Specifications",
                    50.0,
                    100.0,
                    280.0,
                    120.0,
                    font_size=16.0,
                    bold=True,
                ),
            ),
        )
        doc = ParsedDocument(pages=(page1, page2), source_path="test_manual.pdf")

        batch_cir: LayoutCIR = zoner.segment_layout(doc)
        stream_pages: list[PageLayoutCIR] = list(zoner.segment_stream(doc))

        assert len(batch_cir.pages) == len(stream_pages)
        for p_batch, p_stream in zip(batch_cir.pages, stream_pages, strict=True):
            assert p_batch.model_dump() == p_stream.model_dump()
