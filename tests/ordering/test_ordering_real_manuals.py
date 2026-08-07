"""Real-World Workshop Manual Tests for Reading Order Engine (Stage 2.1).

RFC-008: Real-world manual validation against Suzuki F8D Workshop Manual dual-column
repair procedures, Maruti Suzuki K10B exploded diagrams with captions,
and cross-page procedural continuity.
"""

from __future__ import annotations

from mechai.contracts.layout import (
    ColumnGutter,
    LayoutCIR,
    LayoutRegion,
    PageLayoutCIR,
    PageMargins,
    RegionType,
)
from mechai.contracts.ordering import (
    FlowEdgeType,
    ReadingFlowType,
)
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.ordering.sorter import ReadingOrderEngine


def _make_manual_region(
    reg_id: str,
    top: float,
    left: float,
    bottom: float,
    right: float,
    reg_type: RegionType,
    text: str,
    zone_id: str | None = None,
    col_idx: int | None = None,
    page_num: int = 1,
) -> LayoutRegion:
    bbox = BoundingBox(left=left, top=top, right=right, bottom=bottom)
    return LayoutRegion(
        id=reg_id,
        bbox=bbox,
        page_number=page_num,
        region_type=reg_type,
        confidence=0.96,
        provenance=SourceRef(
            page_number=page_num,
            extraction_method=ExtractionMethod.RULE,
            confidence=0.96,
            bbox=bbox,
        ),
        text=text,
        reading_zone_id=zone_id,
        column_index=col_idx,
    )


class TestSuzukiF8DManualReadingOrder:
    """Validate reading order preservation for Suzuki F8D Workshop Manual procedures."""

    def test_f8d_dual_column_procedure_with_warning_and_note(self) -> None:
        """Suzuki F8D 2-column overhaul procedure with numbered steps, warning box, and note box."""
        engine = ReadingOrderEngine()
        gutter = ColumnGutter(left=295.0, right=315.0, top=50.0, bottom=740.0)

        # 1. Running Header
        header = _make_manual_region(
            "f8d_hdr",
            top=20.0,
            left=50.0,
            bottom=38.0,
            right=560.0,
            reg_type=RegionType.HEADER,
            text="ENGINE MECHANICAL (F8D) 6A-15",
            zone_id="zone_header",
        )

        # 2. Spanning Section Title
        title = _make_manual_region(
            "f8d_title",
            top=50.0,
            left=50.0,
            bottom=80.0,
            right=560.0,
            reg_type=RegionType.TITLE,
            text="CYLINDER HEAD AND VALVE MECHANISM REMOVAL",
            zone_id="zone_body_span",
        )

        # 3. Column 0 Procedural Steps & Warning Box
        step1 = _make_manual_region(
            "step_01",
            top=100.0,
            left=50.0,
            bottom=140.0,
            right=290.0,
            reg_type=RegionType.LIST,
            text="1) Disconnect negative (-) cable from battery.",
            col_idx=0,
        )
        step2 = _make_manual_region(
            "step_02",
            top=150.0,
            left=50.0,
            bottom=190.0,
            right=290.0,
            reg_type=RegionType.LIST,
            text="2) Drain engine coolant completely.",
            col_idx=0,
        )
        warning_box = _make_manual_region(
            "warn_01",
            top=200.0,
            left=50.0,
            bottom=250.0,
            right=290.0,
            reg_type=RegionType.WARNING_BOX,
            text="WARNING: Never open radiator cap when engine is hot.",
            col_idx=0,
        )

        # 4. Column 1 Procedural Steps & Note Box
        step3 = _make_manual_region(
            "step_03",
            top=100.0,
            left=320.0,
            bottom=140.0,
            right=560.0,
            reg_type=RegionType.LIST,
            text="3) Remove intake manifold assembly.",
            col_idx=1,
        )
        step4 = _make_manual_region(
            "step_04",
            top=150.0,
            left=320.0,
            bottom=190.0,
            right=560.0,
            reg_type=RegionType.LIST,
            text="4) Remove cylinder head bolts in reverse order.",
            col_idx=1,
        )
        note_box = _make_manual_region(
            "note_01",
            top=200.0,
            left=320.0,
            bottom=240.0,
            right=560.0,
            reg_type=RegionType.NOTE_BOX,
            text="NOTE: Store removed bolts in numbered sequence.",
            col_idx=1,
        )

        # 5. Running Footer
        footer = _make_manual_region(
            "f8d_ftr",
            top=760.0,
            left=500.0,
            bottom=775.0,
            right=560.0,
            reg_type=RegionType.FOOTER,
            text="6A-15",
            zone_id="zone_footer",
        )

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            header_zone=header.bbox,
            footer_zone=footer.bbox,
            columns=(gutter,),
            # Scrambled input order to ensure pure algorithmic resolution
            regions=(footer, step4, step1, warning_box, header, title, step3, note_box, step2),
        )

        ordered_page = engine.order_page(page_layout)

        # Order: Title -> Col0 (Step 1, Step 2, Warning) -> Col1 (Step 3, Step 4, Note)
        expected_sequence = (
            "f8d_title",
            "step_01",
            "step_02",
            "warn_01",
            "step_03",
            "step_04",
            "note_01",
        )
        assert ordered_page.primary_sequence == expected_sequence
        assert ordered_page.reading_flow_type == ReadingFlowType.SPANNING_INTERLEAVED

        # Validate graph properties
        graph = ordered_page.reading_order_graph
        assert graph.is_dag is True
        assert graph.topological_sort()[1:8] == list(expected_sequence)

        # Validate Spanning Descent: Title -> Step 1
        descent_edge = next(
            (e for e in graph.edges if e.source_id == "f8d_title" and e.target_id == "step_01"),
            None,
        )
        assert descent_edge is not None
        assert descent_edge.edge_type == FlowEdgeType.SPANNING_DESCENT

        # Validate Column Wrap: Warning (Col 0 bottom) -> Step 3 (Col 1 top)
        wrap_edge = next(
            (e for e in graph.edges if e.source_id == "warn_01" and e.target_id == "step_03"), None
        )
        assert wrap_edge is not None
        assert wrap_edge.edge_type == FlowEdgeType.COLUMN_WRAP

        # Validate Header & Footer Attachments
        hdr_edge = next((e for e in graph.edges if e.source_id == "f8d_hdr"), None)
        assert hdr_edge is not None
        assert hdr_edge.edge_type == FlowEdgeType.HEADER_ATTACHMENT

        ftr_edge = next((e for e in graph.edges if e.target_id == "f8d_ftr"), None)
        assert ftr_edge is not None
        assert ftr_edge.edge_type == FlowEdgeType.FOOTER_ATTACHMENT


class TestK10BManualReadingOrder:
    """Validate reading order for Maruti Suzuki K10B Engine Manual diagrams and tables."""

    def test_k10b_section_diagram_caption_and_specs_table(self) -> None:
        """K10B: Title -> Exploded Diagram -> Caption -> Spec Table -> Notes."""
        engine = ReadingOrderEngine()
        gutter = ColumnGutter(left=295.0, right=315.0, top=50.0, bottom=740.0)

        # 1. Spanning Section Title
        title = _make_manual_region(
            "k10b_sec",
            top=50.0,
            left=50.0,
            bottom=85.0,
            right=560.0,
            reg_type=RegionType.TITLE,
            text="1D-8 CRANKSHAFT AND CYLINDER BLOCK ASSEMBLY",
            zone_id="zone_body_span",
        )

        # 2. Spanning Exploded Diagram Figure
        fig = _make_manual_region(
            "k10b_fig",
            top=100.0,
            left=50.0,
            bottom=300.0,
            right=560.0,
            reg_type=RegionType.FIGURE_REGION,
            text="[Exploded View of Crankshaft Components]",
            zone_id="zone_body_span",
        )

        # 3. Figure Caption
        caption = _make_manual_region(
            "k10b_cap",
            top=305.0,
            left=50.0,
            bottom=325.0,
            right=560.0,
            reg_type=RegionType.CAPTION,
            text="Fig. 1D-8: Exploded View of Crankshaft and Main Bearings",
            zone_id="zone_body_span",
        )

        # 4. Spanning Specification Table
        table = _make_manual_region(
            "k10b_tbl",
            top=340.0,
            left=50.0,
            bottom=480.0,
            right=560.0,
            reg_type=RegionType.TABLE_REGION,
            text="Bearing Journal | Oil Clearance | Diameter",
            zone_id="zone_body_span",
        )

        # 5. Dual Column Notes below table
        note_c0 = _make_manual_region(
            "k10b_nc0",
            top=500.0,
            left=50.0,
            bottom=580.0,
            right=290.0,
            reg_type=RegionType.PARAGRAPH,
            text="Measure journal diameter using micrometer.",
            col_idx=0,
        )
        note_c1 = _make_manual_region(
            "k10b_nc1",
            top=500.0,
            left=320.0,
            bottom=580.0,
            right=560.0,
            reg_type=RegionType.PARAGRAPH,
            text="Tighten bearing cap bolts to specified torque: 55 N*m.",
            col_idx=1,
        )

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            columns=(gutter,),
            regions=(table, note_c1, title, fig, note_c0, caption),
        )

        ordered_page = engine.order_page(page_layout)

        expected_sequence = ("k10b_sec", "k10b_fig", "k10b_cap", "k10b_tbl", "k10b_nc0", "k10b_nc1")
        assert ordered_page.primary_sequence == expected_sequence

        # Verify Figure to Caption link
        fig_cap_edge = next(
            (
                e
                for e in ordered_page.reading_order_graph.edges
                if e.source_id == "k10b_fig" and e.target_id == "k10b_cap"
            ),
            None,
        )
        assert fig_cap_edge is not None
        assert fig_cap_edge.edge_type == FlowEdgeType.CAPTION_LINK


class TestMultiPageContinuity:
    """Validate multi-page procedural flow with cross-page graph stitching."""

    def test_two_page_continuous_procedure(self) -> None:
        """Exit node of Page 1 must connect with CROSS_PAGE_FLOW to entry node of Page 2."""
        engine = ReadingOrderEngine()

        p1_r1 = _make_manual_region(
            "p1_r1",
            top=100.0,
            left=50.0,
            bottom=200.0,
            right=500.0,
            reg_type=RegionType.PARAGRAPH,
            text="Page 1 Step 1",
            page_num=1,
        )
        p1_r2 = _make_manual_region(
            "p1_r2",
            top=220.0,
            left=50.0,
            bottom=320.0,
            right=500.0,
            reg_type=RegionType.PARAGRAPH,
            text="Page 1 Step 2",
            page_num=1,
        )

        p2_r1 = _make_manual_region(
            "p2_r1",
            top=100.0,
            left=50.0,
            bottom=200.0,
            right=500.0,
            reg_type=RegionType.PARAGRAPH,
            text="Page 2 Step 3",
            page_num=2,
        )
        p2_r2 = _make_manual_region(
            "p2_r2",
            top=220.0,
            left=50.0,
            bottom=320.0,
            right=500.0,
            reg_type=RegionType.PARAGRAPH,
            text="Page 2 Step 4",
            page_num=2,
        )

        p1 = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            regions=(p1_r1, p1_r2),
        )
        p2 = PageLayoutCIR(
            page_number=2,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            regions=(p2_r1, p2_r2),
        )

        doc_layout = LayoutCIR(
            document_id="doc_multipage",
            total_pages=2,
            pages=(p1, p2),
            regions=(p1_r1, p1_r2, p2_r1, p2_r2),
        )

        ordered_doc = engine.order_layout(doc_layout)

        # Global reading order sequence
        assert ordered_doc.global_graph.primary_path == ("p1_r1", "p1_r2", "p2_r1", "p2_r2")

        # Verify CrossPageFlow edge from p1_r2 to p2_r1
        cross_edge = next(
            (
                e
                for e in ordered_doc.global_graph.edges
                if e.source_id == "p1_r2" and e.target_id == "p2_r1"
            ),
            None,
        )
        assert cross_edge is not None
        assert cross_edge.edge_type == FlowEdgeType.CROSS_PAGE_FLOW
        assert cross_edge.evidence.decision_rule == "cross_page_continuation"
