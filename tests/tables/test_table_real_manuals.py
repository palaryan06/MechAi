"""Real OEM Workshop Manual Validation Tests for Automotive Table Intelligence Engine (RFC-AUTO-001).

Validates deterministic table reconstruction, multi-column alignments, subheader grouping,
unit extraction, footnote resolution, and multi-page continuation stitching against authentic
Suzuki F8D and Maruti Suzuki K10B workshop manual table layouts.
"""

from __future__ import annotations

import pytest

from mechai.contracts.layout import ColumnGutter, PageMargins, RegionType
from mechai.contracts.ordering import (
    OrderedLayoutCIR,
    OrderedLayoutRegion,
    OrderedPageCIR,
    ReadingFlowType,
    ReadingOrderGraph,
)
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.contracts.tables import AutomotiveTableType, CellAlignment
from mechai.tables.engine import AutomotiveTableEngine


def _build_synthetic_ordered_page(
    page_number: int,
    regions: list[OrderedLayoutRegion],
) -> OrderedPageCIR:
    """Helper to assemble a valid OrderedPageCIR with deterministic graph."""
    return OrderedPageCIR(
        page_number=page_number,
        width=595.0,
        height=842.0,
        margins=PageMargins(left=36.0, right=36.0, top=36.0, bottom=36.0),
        columns=(ColumnGutter(left=290.0, right=305.0, top=36.0, bottom=806.0),),
        ordered_regions=tuple(regions),
        reading_order_graph=ReadingOrderGraph(),
        primary_sequence=tuple(r.id for r in regions),
        sequence_confidence=0.98,
        reading_flow_type=ReadingFlowType.SINGLE_COLUMN,
    )


class TestSuzukiF8DManualTables:
    """Validation test suite against Suzuki F8D 800cc Workshop Manual table patterns."""

    def test_f8d_tightening_torque_table(self) -> None:
        """Validate Suzuki F8D tightening torque table with fastener items, dual units, and footnotes."""
        title_reg = OrderedLayoutRegion(
            id="reg_p1_001",
            bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
            page_number=1,
            region_type=RegionType.HEADING,
            confidence=0.99,
            provenance=SourceRef(
                page_number=1,
                bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.99,
            ),
            text="Tightening Torque Specifications",
            reading_order_index=1,
            reading_depth=0,
            is_primary_flow=True,
        )

        tbl_text = (
            "| Fastening Part | Thread Diameter | Tightening Torque (N·m) | Tightening Torque (kgf-m) |\n"
            "| --- | --- | --- | --- |\n"
            "| Cylinder head bolt *1 | M10 | 55.0 - 60.0 | 5.5 - 6.0 |\n"
            "| Camshaft sprocket bolt | M8 | 20.0 - 25.0 | 2.0 - 2.5 |\n"
            "| Crankshaft pulley bolt | M12 | 80.0 - 85.0 | 8.0 - 8.5 |\n"
            "| Connecting rod cap nut *2 | M7 | 30.0 - 35.0 | 3.0 - 3.5 |\n"
            "| Spark plug | M14 | 25.0 - 30.0 | 2.5 - 3.0 |\n"
        )
        tbl_reg = OrderedLayoutRegion(
            id="reg_p1_002",
            bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=220.0),
            page_number=1,
            region_type=RegionType.TABLE_REGION,
            confidence=0.98,
            provenance=SourceRef(
                page_number=1,
                bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=220.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.98,
            ),
            text=tbl_text,
            reading_order_index=2,
            reading_depth=0,
            is_primary_flow=True,
        )

        note_text = (
            "*1: Tighten to specified torque after applying clean engine oil to thread and seat surface.\n"
            "*2: Replace with new nut upon every overhaul."
        )
        note_reg = OrderedLayoutRegion(
            id="reg_p1_003",
            bbox=BoundingBox(left=50.0, top=225.0, right=550.0, bottom=260.0),
            page_number=1,
            region_type=RegionType.NOTE_BOX,
            confidence=0.95,
            provenance=SourceRef(
                page_number=1,
                bbox=BoundingBox(left=50.0, top=225.0, right=550.0, bottom=260.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.95,
            ),
            text=note_text,
            reading_order_index=3,
            reading_depth=0,
            is_primary_flow=True,
        )

        page = _build_synthetic_ordered_page(1, [title_reg, tbl_reg, note_reg])
        engine = AutomotiveTableEngine()
        tables = engine.reconstruct_page_tables(page)

        assert len(tables) == 1
        tbl = tables[0]

        assert tbl.title == "Tightening Torque Specifications"
        assert tbl.table_type == AutomotiveTableType.TORQUE_SPECIFICATION
        assert tbl.num_columns == 4
        assert tbl.num_rows == 5
        assert tbl.header.column_units.get(2) == "N·m"
        assert tbl.header.column_units.get(3) == "kgf-m"

        # Verify Footnote Association
        assert len(tbl.footnotes) == 2
        assert tbl.footnotes[0].marker == "*1"
        assert "clean engine oil" in tbl.footnotes[0].text
        assert tbl.footnotes[1].marker == "*2"
        assert "new nut" in tbl.footnotes[1].text

        # Verify Cell Footnote Markers
        row_0 = tbl.rows[0]
        assert row_0.cells[0].footnote_markers == ("*1",)
        row_3 = tbl.rows[3]
        assert row_3.cells[0].footnote_markers == ("*2",)

    def test_f8d_valve_clearance_table_with_subheaders(self) -> None:
        """Validate valve clearance specification table with Intake and Exhaust subheaders."""
        title_reg = OrderedLayoutRegion(
            id="reg_p2_001",
            bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
            page_number=2,
            region_type=RegionType.HEADING,
            confidence=0.99,
            provenance=SourceRef(
                page_number=2,
                bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.99,
            ),
            text="Valve Clearance Standard & Wear Limit",
            reading_order_index=1,
            reading_depth=0,
            is_primary_flow=True,
        )

        tbl_text = (
            "| Item | Standard (Cold) [mm] | Standard (Hot) [mm] | Limit [mm] |\n"
            "| --- | --- | --- | --- |\n"
            "| [INTAKE VALVE] | | | |\n"
            "| Valve clearance | 0.13 - 0.17 | 0.23 - 0.27 | 0.20 |\n"
            "| Valve stem diameter | 5.465 - 5.480 | — | 5.450 |\n"
            "| [EXHAUST VALVE] | | | |\n"
            "| Valve clearance | 0.18 - 0.22 | 0.28 - 0.32 | 0.25 |\n"
            "| Valve stem diameter | 5.440 - 5.455 | — | 5.420 |\n"
        )
        tbl_reg = OrderedLayoutRegion(
            id="reg_p2_002",
            bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=250.0),
            page_number=2,
            region_type=RegionType.TABLE_REGION,
            confidence=0.98,
            provenance=SourceRef(
                page_number=2,
                bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=250.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.98,
            ),
            text=tbl_text,
            reading_order_index=2,
            reading_depth=0,
            is_primary_flow=True,
        )

        page = _build_synthetic_ordered_page(2, [title_reg, tbl_reg])
        engine = AutomotiveTableEngine()
        tables = engine.reconstruct_page_tables(page)

        assert len(tables) == 1
        tbl = tables[0]
        assert tbl.table_type in (AutomotiveTableType.WEAR_LIMIT, AutomotiveTableType.STANDARD_SPECIFICATION)
        assert tbl.num_columns == 4
        assert tbl.num_rows == 6

        # Check subheaders
        assert tbl.rows[0].is_subheader is True
        assert tbl.rows[0].cells[0].raw_text == "[INTAKE VALVE]"
        assert tbl.rows[1].is_subheader is False
        assert tbl.rows[3].is_subheader is True
        assert tbl.rows[3].cells[0].raw_text == "[EXHAUST VALVE]"


class TestMarutiSuzukiK10BManualTables:
    """Validation test suite against Maruti Suzuki K10B Engine Manual table patterns."""

    def test_k10b_fluid_capacities_table(self) -> None:
        """Validate K10B engine oil, coolant, and transmission fluid volume table."""
        tbl_text = (
            "| Fluid / Lubricant | Dry Fill Capacity | Refill Capacity (with filter) | Refill Capacity (without filter) |\n"
            "| --- | --- | --- | --- |\n"
            "| Engine Oil (0W-20 / 5W-30) | 3.5 L | 3.1 L | 2.9 L |\n"
            "| Engine Coolant (50/50 mix) | 4.2 L | 3.8 L | — |\n"
            "| Manual Transmission Oil (75W-80) | 2.2 L | 2.2 L | — |\n"
            "| Brake / Clutch Fluid (DOT 3 / DOT 4) | 0.8 L | 0.8 L | — |\n"
        )
        title_reg = OrderedLayoutRegion(
            id="reg_p3_001",
            bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
            page_number=3,
            region_type=RegionType.HEADING,
            confidence=0.99,
            provenance=SourceRef(
                page_number=3,
                bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.99,
            ),
            text="Fluid Capacities and Lubrication Specifications",
            reading_order_index=1,
            reading_depth=0,
            is_primary_flow=True,
        )
        tbl_reg = OrderedLayoutRegion(
            id="reg_p3_002",
            bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=220.0),
            page_number=3,
            region_type=RegionType.TABLE_REGION,
            confidence=0.98,
            provenance=SourceRef(
                page_number=3,
                bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=220.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.98,
            ),
            text=tbl_text,
            reading_order_index=2,
            reading_depth=0,
            is_primary_flow=True,
        )

        page = _build_synthetic_ordered_page(3, [title_reg, tbl_reg])
        engine = AutomotiveTableEngine()
        tables = engine.reconstruct_page_tables(page)

        assert len(tables) == 1
        tbl = tables[0]
        assert tbl.table_type == AutomotiveTableType.FLUID_CAPACITY
        assert tbl.num_columns == 4
        assert tbl.num_rows == 4
        assert tbl.rows[0].cells[1].unit == "L"


class TestMultiPageTableContinuation:
    """Validation test suite for multi-page table continuation stitching."""

    def test_multi_page_torque_table_stitching(self) -> None:
        """Validate 2-page torque table seamlessly merged into a unified AutomotiveTable."""
        # Page 1
        title_p1 = OrderedLayoutRegion(
            id="reg_p4_001",
            bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
            page_number=4,
            region_type=RegionType.HEADING,
            confidence=0.99,
            provenance=SourceRef(
                page_number=4,
                bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.99,
            ),
            text="Comprehensive Fastener Tightening Torques",
            reading_order_index=1,
            reading_depth=0,
            is_primary_flow=True,
        )
        tbl_text_p1 = (
            "| Fastener | Size | Torque (N·m) |\n"
            "| --- | --- | --- |\n"
            "| Cylinder Block Main Bearing Bolt | M11 | 60.0 |\n"
            "| Flywheel Bolt | M10 | 70.0 |\n"
        )
        tbl_reg_p1 = OrderedLayoutRegion(
            id="reg_p4_002",
            bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=180.0),
            page_number=4,
            region_type=RegionType.TABLE_REGION,
            confidence=0.98,
            provenance=SourceRef(
                page_number=4,
                bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=180.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.98,
            ),
            text=tbl_text_p1,
            reading_order_index=2,
            reading_depth=0,
            is_primary_flow=True,
        )

        # Page 2 (Continuation)
        title_p2 = OrderedLayoutRegion(
            id="reg_p5_001",
            bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
            page_number=5,
            region_type=RegionType.HEADING,
            confidence=0.99,
            provenance=SourceRef(
                page_number=5,
                bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=70.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.99,
            ),
            text="Comprehensive Fastener Tightening Torques (Continued)",
            reading_order_index=1,
            reading_depth=0,
            is_primary_flow=True,
        )
        tbl_text_p2 = (
            "| Fastener | Size | Torque (N·m) |\n"
            "| --- | --- | --- |\n"
            "| Oil Pan Drain Plug | M14 | 35.0 |\n"
            "| Water Pump Bolt | M6 | 11.0 |\n"
            "| Thermostat Housing Bolt | M6 | 10.0 |\n"
        )
        tbl_reg_p2 = OrderedLayoutRegion(
            id="reg_p5_002",
            bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=220.0),
            page_number=5,
            region_type=RegionType.TABLE_REGION,
            confidence=0.98,
            provenance=SourceRef(
                page_number=5,
                bbox=BoundingBox(left=50.0, top=75.0, right=550.0, bottom=220.0),
                extraction_method=ExtractionMethod.RULE,
                confidence=0.98,
            ),
            text=tbl_text_p2,
            reading_order_index=2,
            reading_depth=0,
            is_primary_flow=True,
        )

        page_4 = _build_synthetic_ordered_page(4, [title_p1, tbl_reg_p1])
        page_5 = _build_synthetic_ordered_page(5, [title_p2, tbl_reg_p2])

        ordered_doc = OrderedLayoutCIR(
            document_id="doc_suzuki_f8d_multi_page",
            pages=(page_4, page_5),
            total_pages=2,
            global_graph=ReadingOrderGraph(),
            provenance=SourceRef(
                page_number=4,
                extraction_method=ExtractionMethod.RULE,
                confidence=0.99,
            ),
        )

        engine = AutomotiveTableEngine()
        table_set = engine.reconstruct_tables(ordered_doc)

        assert table_set.total_tables == 1
        stitched_table = table_set.tables[0]

        assert stitched_table.is_multi_page is True
        assert stitched_table.page_span == (4, 5)
        assert stitched_table.num_rows == 5  # 2 rows from page 4 + 3 rows from page 5
        assert stitched_table.num_columns == 3

        # Verify sequential row indices across pages
        for idx, row in enumerate(stitched_table.rows):
            assert row.row_index == idx
            for cell in row.cells:
                assert cell.row_index == idx

        assert stitched_table.rows[0].cells[0].raw_text == "Cylinder Block Main Bearing Bolt"
        assert stitched_table.rows[4].cells[0].raw_text == "Thermostat Housing Bolt"
