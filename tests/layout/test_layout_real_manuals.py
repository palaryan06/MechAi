"""Validation test suite against real-world automotive manual layout structures.

Covers layout structures and challenging edge cases modeled after:
1. Maruti Suzuki K10B Engine Service Manual (Exploded views, torque matrices, landscape specs)
2. Suzuki F8D Workshop Manual (2-column repair procedures, warning callouts, notes)
"""

from __future__ import annotations

from mechai.contracts.layout import RegionType
from mechai.contracts.provenance import BoundingBox
from mechai.contracts.scrubbing import (
    ParsedDocument,
    ParsedImage,
    ParsedPage,
    ParsedWord,
)
from mechai.layout import GeometricLayoutZoner, LayoutEngineFactory


def _word(
    text: str,
    left: float,
    top: float,
    right: float,
    bottom: float,
    font_size: float = 10.0,
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
        font_name="Helvetica-Bold" if bold else "Helvetica",
        bold=bold,
        italic=italic,
    )


class TestK10BManualLayout:
    """Validation test suite on K10B Engine Manual layout structures."""

    def test_k10b_section_header_and_exploded_view_figure(self) -> None:
        """K10B manual page with header, diagram, callout caption, and torque table."""
        zoner = GeometricLayoutZoner()

        # Running Header
        header_words = [
            _word(
                "ENGINE MECHANICAL (K10B ENGINE)",
                50.0,
                25.0,
                240.0,
                37.0,
                font_size=9.0,
                bold=True,
            ),
            _word("1D-14", 530.0, 25.0, 560.0, 37.0, font_size=9.0, bold=True),
        ]

        # Section Title
        title_words = [
            _word(
                "CYLINDER HEAD AND VALVES",
                50.0,
                60.0,
                300.0,
                78.0,
                font_size=16.0,
                bold=True,
            ),
        ]

        # Exploded diagram image
        exploded_view_img = ParsedImage(
            image_id="img_k10b_cyl_head",
            bbox=BoundingBox(left=50.0, top=90.0, right=350.0, bottom=300.0),
            width=300,
            height=210,
            image_format="png",
        )

        # Diagram Caption
        caption_words = [
            _word(
                "Fig. 1D-8: Cylinder Head Exploded View",
                50.0,
                310.0,
                260.0,
                322.0,
                font_size=9.0,
                bold=True,
            ),
        ]

        # Specification Table (Right side / below)
        table_words = [
            _word("Fastener", 50.0, 350.0, 110.0, 362.0, font_size=9.0, bold=True),
            _word(
                "Torque (N-m)",
                200.0,
                350.0,
                280.0,
                362.0,
                font_size=9.0,
                bold=True,
            ),
            _word(
                "Torque (kg-m)",
                350.0,
                350.0,
                430.0,
                362.0,
                font_size=9.0,
                bold=True,
            ),
            _word("Cylinder Head Bolt", 50.0, 370.0, 150.0, 382.0, font_size=9.0),
            _word("55.0 N-m", 200.0, 370.0, 250.0, 382.0, font_size=9.0),
            _word("5.5 kg-m", 350.0, 370.0, 400.0, 382.0, font_size=9.0),
            _word("Camshaft Cap Bolt", 50.0, 390.0, 150.0, 402.0, font_size=9.0),
            _word("11.0 N-m", 200.0, 390.0, 250.0, 402.0, font_size=9.0),
            _word("1.1 kg-m", 350.0, 390.0, 400.0, 402.0, font_size=9.0),
        ]

        page = ParsedPage(
            page_number=14,
            width=612.0,
            height=792.0,
            words=tuple(header_words + title_words + caption_words + table_words),
            images=(exploded_view_img,),
        )

        doc = ParsedDocument(
            pages=(page,),
            source_path="K10B_Engine_Service_Manual.pdf",
        )
        layout_cir = zoner.segment_layout(doc)

        p14 = layout_cir.pages[0]
        region_types = {r.region_type for r in p14.regions}

        assert RegionType.HEADER in region_types
        assert RegionType.TITLE in region_types
        assert RegionType.FIGURE_REGION in region_types
        assert RegionType.CAPTION in region_types
        assert RegionType.TABLE_REGION in region_types

        # Verify Figure Region bbox matches image
        fig = next(r for r in p14.regions if r.region_type == RegionType.FIGURE_REGION)
        assert fig.bbox.left == 50.0
        assert fig.bbox.top == 90.0
        assert fig.confidence >= 0.90


class TestSuzukiF8DManualLayout:
    """Validation test suite on Suzuki F8D Workshop Manual layout structures."""

    def test_f8d_dual_column_procedure_with_warning_and_note(self) -> None:
        """F8D 2-column overhaul procedure with numbered steps, warning, and torque note."""
        zoner = GeometricLayoutZoner()

        # Running Header
        header = [
            _word(
                "1E-8 CRANKSHAFT AND CYLINDER BLOCK",
                50.0,
                25.0,
                260.0,
                37.0,
                font_size=9.0,
            ),
            _word("Page 1E-8", 510.0, 25.0, 560.0, 37.0, font_size=9.0),
        ]

        # Column 1: Numbered overhaul procedure steps (left: 50..260)
        col1_steps = [
            _word(
                "Disassembly Procedure",
                50.0,
                80.0,
                180.0,
                93.0,
                font_size=12.0,
                bold=True,
            ),
            _word("1.", 50.0, 105.0, 60.0, 117.0, font_size=10.0),
            _word(
                "Remove oil pan and strainer.",
                65.0,
                105.0,
                250.0,
                117.0,
                font_size=10.0,
            ),
            _word("2.", 50.0, 130.0, 60.0, 142.0, font_size=10.0),
            _word(
                "Remove rod cap nuts.",
                65.0,
                130.0,
                240.0,
                142.0,
                font_size=10.0,
            ),
            _word("3.", 50.0, 155.0, 60.0, 167.0, font_size=10.0),
            _word(
                "Extract piston assembly.",
                65.0,
                155.0,
                245.0,
                167.0,
                font_size=10.0,
            ),
        ]

        # Column 2: Safety Warning Box & Note Box (left: 320..550, Gutter: 260..320)
        col2_boxes = [
            _word("WARNING:", 320.0, 80.0, 380.0, 93.0, font_size=10.5, bold=True),
            _word(
                "Do not damage crankshaft journal surfaces.",
                385.0,
                80.0,
                550.0,
                110.0,
                font_size=10.0,
            ),
            _word("NOTE:", 320.0, 130.0, 360.0, 143.0, font_size=10.0, bold=True),
            _word(
                "Arrange removed bearings in order.",
                365.0,
                130.0,
                550.0,
                160.0,
                font_size=10.0,
            ),
        ]

        # Running Footer
        footer = [
            _word(
                "SUZUKI F8D WORKSHOP MANUAL 99500-84E00-01E",
                160.0,
                760.0,
                450.0,
                772.0,
                font_size=8.0,
            ),
        ]

        page = ParsedPage(
            page_number=8,
            width=612.0,
            height=792.0,
            words=tuple(header + col1_steps + col2_boxes + footer),
        )

        doc = ParsedDocument(
            pages=(page,),
            source_path="Suzuki_F8D_Workshop_Manual.pdf",
        )
        layout_cir = zoner.segment_layout(doc)

        p8 = layout_cir.pages[0]

        # Verify multi-column detection detected the gutter between column 1 and column 2
        assert len(p8.columns) >= 1
        gutter = p8.columns[0]
        assert gutter.left >= 240.0
        assert gutter.right <= 330.0

        # Verify regions
        types = {r.region_type for r in p8.regions}
        assert RegionType.HEADER in types
        assert RegionType.FOOTER in types
        assert RegionType.WARNING_BOX in types
        assert RegionType.NOTE_BOX in types
        assert RegionType.LIST in types or RegionType.PARAGRAPH in types

        # Check warning box text & confidence
        warn = next(r for r in p8.regions if r.region_type == RegionType.WARNING_BOX)
        assert "WARNING:" in warn.text
        assert warn.confidence >= 0.94

        # Check note box text & confidence
        note = next(r for r in p8.regions if r.region_type == RegionType.NOTE_BOX)
        assert "NOTE:" in note.text
        assert note.confidence >= 0.93


class TestFailureAndEdgeCases:
    """Document and validate edge cases and boundary conditions."""

    def test_single_isolated_word_page(self) -> None:
        """Page with only a single word (e.g. blank appendix separator)."""
        zoner = LayoutEngineFactory.create()
        word = _word("APPENDIX", 250.0, 380.0, 350.0, 400.0, font_size=20.0, bold=True)
        page = ParsedPage(page_number=1, width=612.0, height=792.0, words=(word,))
        layout = zoner.segment_page(page)

        assert len(layout.regions) == 1
        assert layout.regions[0].region_type in (
            RegionType.TITLE,
            RegionType.HEADING,
            RegionType.BODY,
        )

    def test_overlapping_words_and_unaligned_text_resilience(self) -> None:
        """Page with noisy coordinates from scanned manual artifacts."""
        zoner = LayoutEngineFactory.create()
        noisy_words = [
            _word("WordA", 100.0, 200.0, 150.0, 212.0),
            _word("WordB", 148.0, 201.0, 190.0, 213.0),
            _word("WordC", 195.0, 199.0, 240.0, 211.0),
        ]
        page = ParsedPage(
            page_number=1,
            width=612.0,
            height=792.0,
            words=tuple(noisy_words),
        )
        layout = zoner.segment_page(page)

        assert len(layout.regions) == 1
        assert "WordA WordB WordC" in layout.regions[0].text
