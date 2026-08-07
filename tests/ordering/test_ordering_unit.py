"""Comprehensive Unit Tests for Reading Order Engine (Stage 2.1).

RFC-008: Validates DAG topologies, multi-column traversal, spanning elements,
figure-caption binding, callout priority insertion, sidebars, and streaming parity.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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
    OrderedLayoutEngineProtocol,
    OrderedLayoutRegion,
    ReadingFlowType,
    ReadingOrderEngineProtocol,
    ReadingOrderEvidence,
    ReadingOrderNode,
)
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.ordering.factory import ReadingOrderEngineFactory
from mechai.ordering.graph import ReadingOrderGraphBuilder
from mechai.ordering.sorter import ReadingOrderEngine


def _make_region(
    reg_id: str,
    top: float,
    left: float,
    bottom: float,
    right: float,
    reg_type: RegionType = RegionType.PARAGRAPH,
    text: str = "",
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
        confidence=0.95,
        provenance=SourceRef(
            page_number=page_num,
            extraction_method=ExtractionMethod.RULE,
            confidence=0.95,
            bbox=bbox,
        ),
        text=text or f"Sample text for {reg_id}",
        reading_zone_id=zone_id,
        column_index=col_idx,
    )


class TestReadingOrderContracts:
    """Validate data contract structures, enums, and immutability."""

    def test_all_flow_edge_types_exist(self) -> None:
        """Verify all 10 expected flow edge types exist in enum."""
        expected = {
            "NaturalFlow",
            "ColumnWrap",
            "SpanningDescent",
            "SpanningAscent",
            "CaptionLink",
            "CalloutAside",
            "SidebarBranch",
            "CrossPageFlow",
            "HeaderAttachment",
            "FooterAttachment",
        }
        actual = {et.value for et in FlowEdgeType}
        assert expected == actual

    def test_all_reading_flow_types_exist(self) -> None:
        """Verify reading flow type enums."""
        expected = {
            "SingleColumn",
            "MultiColumnWrap",
            "SpanningInterleaved",
            "SidebarInterrupted",
            "ComplexIrregular",
        }
        actual = {ft.value for ft in ReadingFlowType}
        assert expected == actual

    def test_ordered_region_immutability(self) -> None:
        """Verify OrderedLayoutRegion is frozen and immutable."""
        bbox = BoundingBox(left=50.0, top=50.0, right=200.0, bottom=100.0)
        reg = OrderedLayoutRegion(
            id="reg_01",
            bbox=bbox,
            page_number=1,
            region_type=RegionType.PARAGRAPH,
            confidence=0.95,
            provenance=SourceRef(page_number=1, confidence=0.95, bbox=bbox),
            text="Text",
            reading_order_index=1,
            reading_depth=0,
            is_primary_flow=True,
        )
        with pytest.raises(ValidationError):
            setattr(reg, "reading_order_index", 2)


class TestReadingOrderGraph:
    """Validate DAG construction, cycle elimination, and topological sorting."""

    def test_graph_dag_verification_and_topological_sort(self) -> None:
        """Graph builder correctly constructs a DAG and derives topological sequence."""
        builder = ReadingOrderGraphBuilder()
        bbox = BoundingBox(left=50.0, top=50.0, right=200.0, bottom=100.0)

        for i in range(1, 4):
            builder.add_node(
                ReadingOrderNode(
                    region_id=f"n{i}",
                    page_number=1,
                    region_type=RegionType.PARAGRAPH,
                    bbox=bbox,
                    order_index=i,
                )
            )

        evidence = ReadingOrderEvidence(
            decision_rule="vertical_flow",
            source_zone="col0",
            target_zone="col0",
            spatial_distance_pt=10.0,
            confidence=0.95,
            rationale="Flow down col 0",
        )
        builder.add_edge("n1", "n2", FlowEdgeType.NATURAL_FLOW, 0.95, evidence)
        builder.add_edge("n2", "n3", FlowEdgeType.NATURAL_FLOW, 0.95, evidence)
        builder.set_primary_path(["n1", "n2", "n3"])

        graph = builder.build()
        assert graph.is_dag is True
        assert graph.topological_sort() == ["n1", "n2", "n3"]
        assert len(graph.get_outgoing_edges("n1")) == 1
        assert len(graph.get_incoming_edges("n3")) == 1

    def test_cycle_elimination_guarantees_dag(self) -> None:
        """Graph builder eliminates cycle-causing back edges to guarantee DAG validity."""
        builder = ReadingOrderGraphBuilder()
        bbox = BoundingBox(left=50.0, top=50.0, right=200.0, bottom=100.0)

        builder.add_node(
            ReadingOrderNode(
                region_id="A",
                page_number=1,
                region_type=RegionType.PARAGRAPH,
                bbox=bbox,
                order_index=1,
            )
        )
        builder.add_node(
            ReadingOrderNode(
                region_id="B",
                page_number=1,
                region_type=RegionType.PARAGRAPH,
                bbox=bbox,
                order_index=2,
            )
        )
        builder.add_node(
            ReadingOrderNode(
                region_id="C",
                page_number=1,
                region_type=RegionType.PARAGRAPH,
                bbox=bbox,
                order_index=3,
            )
        )

        evidence = ReadingOrderEvidence(
            decision_rule="test",
            source_zone="body",
            target_zone="body",
            spatial_distance_pt=5.0,
            confidence=0.9,
            rationale="test",
        )
        builder.add_edge("A", "B", FlowEdgeType.NATURAL_FLOW, 0.9, evidence)
        builder.add_edge("B", "C", FlowEdgeType.NATURAL_FLOW, 0.9, evidence)
        # Attempt to add cycle edge C -> A
        builder.add_edge("C", "A", FlowEdgeType.NATURAL_FLOW, 0.9, evidence)

        graph = builder.build()
        assert graph.is_dag is True
        # The back edge C -> A should have been rejected
        assert len(graph.edges) == 2


class TestSingleAndMultiColumnOrdering:
    """Validate spatial ordering on single, dual, and three column page layouts."""

    def test_single_column_page_order(self) -> None:
        """Single column page elements should be sorted purely top-to-bottom."""
        engine = ReadingOrderEngine()
        p1 = _make_region(
            "p1", top=100.0, left=50.0, bottom=150.0, right=500.0, reg_type=RegionType.TITLE
        )
        p2 = _make_region(
            "p2", top=180.0, left=50.0, bottom=250.0, right=500.0, reg_type=RegionType.PARAGRAPH
        )
        p3 = _make_region(
            "p3", top=280.0, left=50.0, bottom=350.0, right=500.0, reg_type=RegionType.LIST
        )

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            columns=(),
            regions=(p2, p1, p3),  # un-ordered input
        )

        ordered_page = engine.order_page(page_layout)
        assert ordered_page.primary_sequence == ("p1", "p2", "p3")
        assert ordered_page.reading_flow_type == ReadingFlowType.SINGLE_COLUMN
        assert ordered_page.reading_order_graph.is_dag is True

    def test_two_column_page_order(self) -> None:
        """Two-column page: Column 0 elements must be read completely before Column 1."""
        engine = ReadingOrderEngine()
        gutter = ColumnGutter(left=295.0, right=315.0, top=50.0, bottom=740.0)

        # Col 0 regions (left=50 to 290)
        c0_top = _make_region("c0_top", top=100.0, left=50.0, bottom=180.0, right=290.0, col_idx=0)
        c0_bot = _make_region("c0_bot", top=200.0, left=50.0, bottom=300.0, right=290.0, col_idx=0)

        # Col 1 regions (left=320 to 560)
        c1_top = _make_region("c1_top", top=100.0, left=320.0, bottom=180.0, right=560.0, col_idx=1)
        c1_bot = _make_region("c1_bot", top=200.0, left=320.0, bottom=300.0, right=560.0, col_idx=1)

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            columns=(gutter,),
            regions=(c1_top, c0_bot, c1_bot, c0_top),  # scrambled
        )

        ordered_page = engine.order_page(page_layout)
        assert ordered_page.primary_sequence == ("c0_top", "c0_bot", "c1_top", "c1_bot")
        assert ordered_page.reading_flow_type == ReadingFlowType.MULTI_COLUMN_WRAP

        # Verify ColumnWrap edge exists from c0_bot to c1_top
        wrap_edge = next(
            (
                e
                for e in ordered_page.reading_order_graph.edges
                if e.source_id == "c0_bot" and e.target_id == "c1_top"
            ),
            None,
        )
        assert wrap_edge is not None
        assert wrap_edge.edge_type == FlowEdgeType.COLUMN_WRAP
        assert "Column wrap" in wrap_edge.evidence.rationale

    def test_three_column_page_order(self) -> None:
        """Three-column layout: Col 0 -> Col 1 -> Col 2."""
        engine = ReadingOrderEngine()
        g1 = ColumnGutter(left=190.0, right=210.0, top=50.0, bottom=740.0)
        g2 = ColumnGutter(left=390.0, right=410.0, top=50.0, bottom=740.0)

        c0 = _make_region("c0", top=100.0, left=50.0, bottom=200.0, right=180.0, col_idx=0)
        c1 = _make_region("c1", top=100.0, left=220.0, bottom=200.0, right=380.0, col_idx=1)
        c2 = _make_region("c2", top=100.0, left=420.0, bottom=200.0, right=560.0, col_idx=2)

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            columns=(g1, g2),
            regions=(c2, c0, c1),
        )

        ordered_page = engine.order_page(page_layout)
        assert ordered_page.primary_sequence == ("c0", "c1", "c2")


class TestSpanningAndCaptionInterleaving:
    """Validate spanning titles, cross-column tables, and caption bindings."""

    def test_spanning_title_and_spanning_table_interleaved(self) -> None:
        """Title (span) -> Band 1 (Col 0, Col 1) -> Table (span) -> Band 2 (Col 0, Col 1)."""
        engine = ReadingOrderEngine()
        gutter = ColumnGutter(left=295.0, right=315.0, top=50.0, bottom=740.0)

        # Spanning Title at top
        title = _make_region(
            "title",
            top=50.0,
            left=50.0,
            bottom=90.0,
            right=560.0,
            reg_type=RegionType.TITLE,
            zone_id="zone_body_span",
        )

        # Band 1 dual columns
        b1_c0 = _make_region("b1_c0", top=110.0, left=50.0, bottom=190.0, right=290.0, col_idx=0)
        b1_c1 = _make_region("b1_c1", top=110.0, left=320.0, bottom=190.0, right=560.0, col_idx=1)

        # Spanning Table in middle
        table = _make_region(
            "table",
            top=210.0,
            left=50.0,
            bottom=350.0,
            right=560.0,
            reg_type=RegionType.TABLE_REGION,
            zone_id="zone_body_span",
        )

        # Band 2 dual columns
        b2_c0 = _make_region("b2_c0", top=370.0, left=50.0, bottom=450.0, right=290.0, col_idx=0)
        b2_c1 = _make_region("b2_c1", top=370.0, left=320.0, bottom=450.0, right=560.0, col_idx=1)

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            columns=(gutter,),
            regions=(b2_c1, b1_c1, table, title, b1_c0, b2_c0),
        )

        ordered_page = engine.order_page(page_layout)
        expected = ("title", "b1_c0", "b1_c1", "table", "b2_c0", "b2_c1")
        assert ordered_page.primary_sequence == expected
        assert ordered_page.reading_flow_type == ReadingFlowType.SPANNING_INTERLEAVED

        # Verify Spanning Descent & Ascent edges
        edges = ordered_page.reading_order_graph.edges
        descent_edge = next(
            (e for e in edges if e.source_id == "title" and e.target_id == "b1_c0"), None
        )
        assert descent_edge is not None
        assert descent_edge.edge_type == FlowEdgeType.SPANNING_DESCENT

        ascent_edge = next(
            (e for e in edges if e.source_id == "b1_c1" and e.target_id == "table"), None
        )
        assert ascent_edge is not None
        assert ascent_edge.edge_type == FlowEdgeType.SPANNING_ASCENT

    def test_figure_and_caption_binding(self) -> None:
        """A Caption immediately below a FigureRegion must be bound with CAPTION_LINK."""
        engine = ReadingOrderEngine()

        fig = _make_region(
            "fig_01",
            top=100.0,
            left=50.0,
            bottom=250.0,
            right=400.0,
            reg_type=RegionType.FIGURE_REGION,
        )
        cap = _make_region(
            "cap_01",
            top=255.0,
            left=50.0,
            bottom=275.0,
            right=400.0,
            reg_type=RegionType.CAPTION,
            text="Fig. 1 Exploded View",
        )
        para = _make_region(
            "para_01",
            top=300.0,
            left=50.0,
            bottom=380.0,
            right=500.0,
            reg_type=RegionType.PARAGRAPH,
        )

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            columns=(),
            regions=(para, cap, fig),
        )

        ordered_page = engine.order_page(page_layout)
        assert ordered_page.primary_sequence == ("fig_01", "cap_01", "para_01")

        cap_edge = next(
            (
                e
                for e in ordered_page.reading_order_graph.edges
                if e.source_id == "fig_01" and e.target_id == "cap_01"
            ),
            None,
        )
        assert cap_edge is not None
        assert cap_edge.edge_type == FlowEdgeType.CAPTION_LINK


class TestSidebarsAndHeadersFooters:
    """Validate sidebars alternative paths and running header/footer detachment."""

    def test_sidebar_creates_alternative_path(self) -> None:
        """Sidebar should be detached from primary sequence and placed in alternative_paths."""
        engine = ReadingOrderEngine()

        p1 = _make_region("p1", top=100.0, left=50.0, bottom=200.0, right=380.0)
        p2 = _make_region("p2", top=220.0, left=50.0, bottom=320.0, right=380.0)
        sidebar = _make_region(
            "sb",
            top=100.0,
            left=420.0,
            bottom=300.0,
            right=560.0,
            reg_type=RegionType.SIDEBAR,
            zone_id="zone_sidebar",
        )

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            columns=(),
            regions=(p1, sidebar, p2),
        )

        ordered_page = engine.order_page(page_layout)
        assert ordered_page.primary_sequence == ("p1", "p2")
        assert len(ordered_page.alternative_paths) == 1
        alt = ordered_page.alternative_paths[0]
        assert alt.region_ids == ("sb",)
        assert ordered_page.reading_flow_type == ReadingFlowType.SIDEBAR_INTERRUPTED

    def test_running_header_and_footer_attachments(self) -> None:
        """Headers and footers are attached as metadata edges outside the primary sequence."""
        engine = ReadingOrderEngine()

        header = _make_region(
            "hdr",
            top=20.0,
            left=50.0,
            bottom=40.0,
            right=550.0,
            reg_type=RegionType.HEADER,
            zone_id="zone_header",
        )
        body = _make_region(
            "body1", top=80.0, left=50.0, bottom=200.0, right=550.0, reg_type=RegionType.PARAGRAPH
        )
        footer = _make_region(
            "ftr",
            top=750.0,
            left=50.0,
            bottom=770.0,
            right=550.0,
            reg_type=RegionType.FOOTER,
            zone_id="zone_footer",
        )

        page_layout = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            header_zone=header.bbox,
            footer_zone=footer.bbox,
            columns=(),
            regions=(header, body, footer),
        )

        ordered_page = engine.order_page(page_layout)
        assert ordered_page.primary_sequence == ("body1",)

        # Verify HeaderAttachment and FooterAttachment edges exist
        hdr_edge = next(
            (
                e
                for e in ordered_page.reading_order_graph.edges
                if e.source_id == "hdr" and e.target_id == "body1"
            ),
            None,
        )
        assert hdr_edge is not None
        assert hdr_edge.edge_type == FlowEdgeType.HEADER_ATTACHMENT

        ftr_edge = next(
            (
                e
                for e in ordered_page.reading_order_graph.edges
                if e.source_id == "body1" and e.target_id == "ftr"
            ),
            None,
        )
        assert ftr_edge is not None
        assert ftr_edge.edge_type == FlowEdgeType.FOOTER_ATTACHMENT


class TestFactoryAndStreamingParity:
    """Validate Factory instantiation and batch/stream equivalence."""

    def test_factory_creation(self) -> None:
        """Factory creates valid engine adhering to ReadingOrderEngineProtocol."""
        engine = ReadingOrderEngineFactory.create()
        assert isinstance(engine, ReadingOrderEngineProtocol)
        assert isinstance(engine, OrderedLayoutEngineProtocol)

    def test_batch_and_streaming_parity(self) -> None:
        """order_layout() and order_stream() must produce identical results."""
        engine = ReadingOrderEngineFactory.create()
        r1 = _make_region("r1", top=100.0, left=50.0, bottom=200.0, right=500.0, page_num=1)
        r2 = _make_region("r2", top=100.0, left=50.0, bottom=200.0, right=500.0, page_num=2)

        p1 = PageLayoutCIR(
            page_number=1,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            regions=(r1,),
        )
        p2 = PageLayoutCIR(
            page_number=2,
            width=612.0,
            height=792.0,
            margins=PageMargins(left=50.0, top=50.0, right=50.0, bottom=50.0),
            regions=(r2,),
        )

        doc_layout = LayoutCIR(
            document_id="doc_test", total_pages=2, pages=(p1, p2), regions=(r1, r2)
        )

        batch_result = engine.order_layout(doc_layout)
        stream_pages = list(engine.order_stream(doc_layout))

        assert len(batch_result.pages) == len(stream_pages)
        for bp, sp in zip(batch_result.pages, stream_pages, strict=True):
            assert bp.primary_sequence == sp.primary_sequence
            assert bp.reading_flow_type == sp.reading_flow_type
            assert len(bp.ordered_regions) == len(sp.ordered_regions)
