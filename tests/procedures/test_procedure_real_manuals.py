"""Real-world automotive manual procedure validation tests (RFC-AUTO-002).

Validates deterministic extraction against OEM workshop manual patterns from:
- Suzuki F8D 800cc Workshop Manual (Cylinder Head & Valve Train Disassembly / Overhaul)
- Maruti Suzuki K10B Engine Service Manual (Timing Chain & Oil Pump Removal / Installation)
- Multi-page continuous procedure stitching across page boundaries, intervening tables and diagrams.
"""

from __future__ import annotations

import pytest

from mechai.contracts.layout import BoundingBox, ExtractionMethod, PageMargins, RegionType, SourceRef
from mechai.contracts.ordering import (
    FlowEdgeType,
    OrderedLayoutCIR,
    OrderedLayoutRegion,
    OrderedPageCIR,
    ReadingFlowType,
    ReadingOrderEdge,
    ReadingOrderEvidence,
    ReadingOrderGraph,
    ReadingOrderNode,
)
from mechai.contracts.procedures import (
    AdmonitionType,
    ProcedureCategory,
    StepNumberingStyle,
)
from mechai.procedures.engine import AutomotiveProcedureEngine


def _make_source_ref(page: int, top: float, bottom: float) -> SourceRef:
    return SourceRef(
        page_number=page,
        bbox=BoundingBox(left=50.0, top=top, right=550.0, bottom=bottom),
        extraction_method=ExtractionMethod.RULE,
        confidence=0.98,
    )


def _make_ordered_region(
    reg_id: str,
    text: str,
    reg_type: RegionType,
    page: int,
    order_idx: int,
    top: float = 100.0,
    bottom: float = 150.0,
) -> OrderedLayoutRegion:
    return OrderedLayoutRegion(
        id=reg_id,
        bbox=BoundingBox(left=50.0, top=top, right=550.0, bottom=bottom),
        page_number=page,
        region_type=reg_type,
        confidence=0.98,
        provenance=_make_source_ref(page, top, bottom),
        text=text,
        reading_order_index=order_idx,
        reading_depth=0,
        is_primary_flow=True,
    )


def _make_ordered_page(page_num: int, regions: list[OrderedLayoutRegion]) -> OrderedPageCIR:
    nodes = [
        ReadingOrderNode(
            region_id=r.id,
            region_type=r.region_type,
            bbox=r.bbox,
            page_number=page_num,
            order_index=r.reading_order_index,
            is_primary_flow=True,
        )
        for r in regions
    ]
    edges: list[ReadingOrderEdge] = []
    for i in range(len(regions) - 1):
        edges.append(
            ReadingOrderEdge(
                source_id=regions[i].id,
                target_id=regions[i + 1].id,
                edge_type=FlowEdgeType.NATURAL_FLOW,
                confidence=0.99,
                evidence=ReadingOrderEvidence(
                    decision_rule="RULE-FLOW",
                    source_zone="Z0",
                    target_zone="Z0",
                    spatial_distance_pt=10.0,
                    confidence=0.99,
                    rationale="Sequential reading flow",
                ),
            )
        )

    graph = ReadingOrderGraph(
        nodes=tuple(nodes),
        edges=tuple(edges),
        primary_path=tuple(r.id for r in regions),
        alternative_paths=(),
    )

    return OrderedPageCIR(
        page_number=page_num,
        width=612.0,
        height=792.0,
        margins=PageMargins(left=36.0, top=36.0, right=36.0, bottom=36.0),
        header_zone=None,
        footer_zone=None,
        columns=(),
        ordered_regions=tuple(regions),
        reading_order_graph=graph,
        primary_sequence=tuple(r.id for r in regions),
        alternative_paths=(),
        sequence_confidence=0.98,
        reading_flow_type=ReadingFlowType.SINGLE_COLUMN,
    )


class TestSuzukiF8DManualProcedures:
    """Test suite validating against Suzuki F8D 800cc Workshop Manual procedures."""

    def test_cylinder_head_disassembly_overhaul(self) -> None:
        regions = [
            _make_ordered_region(
                "h_f8d_01",
                "Cylinder Head Disassembly & Overhaul",
                RegionType.HEADING,
                page=1,
                order_idx=1,
                top=50.0,
                bottom=70.0,
            ),
            _make_ordered_region(
                "pre_f8d_01",
                "Preparation:\nDisconnect negative battery cable.\nDrain engine oil and cooling system.",
                RegionType.BODY,
                page=1,
                order_idx=2,
                top=75.0,
                bottom=110.0,
            ),
            _make_ordered_region(
                "warn_f8d_01",
                "WARNING: Engine coolant may be hot. Allow engine to cool before draining.",
                RegionType.WARNING_BOX,
                page=1,
                order_idx=3,
                top=115.0,
                bottom=145.0,
            ),
            _make_ordered_region(
                "steps_f8d_01",
                "1. Remove intake manifold and exhaust manifold.\n"
                "2. Remove cylinder head cover and distributor.\n"
                "3. Remove rocker arm shaft and rocker arms:\n"
                "   a) Loosen rocker arm shaft securing screws.\n"
                "   b) Pull out rocker arm shaft and remove springs.\n"
                "4. Remove valves and valve springs:\n"
                "   a) Compress valve spring using SST 09916-14510 (Valve spring compressor).\n"
                "   b) Remove valve cotters using tweezers or magnet.\n"
                "   c) Release compressor and remove spring retainer and valve spring.\n"
                "   d) Pull out valve from combustion chamber side.\n"
                "5. Remove valve stem oil seal. Always replace with new valve stem seal.\n"
                "6. Measure valve stem diameter with a micrometer. Refer to Table 6A-2 for wear limits.\n"
                "7. Clean cylinder head mating surface. Always replace cylinder head gasket with new.",
                RegionType.LIST,
                page=1,
                order_idx=4,
                top=150.0,
                bottom=500.0,
            ),
            _make_ordered_region(
                "post_f8d_01",
                "After installation:\nRefill engine oil and coolant. Check for leaks and verify valve clearance.",
                RegionType.BODY,
                page=1,
                order_idx=5,
                top=510.0,
                bottom=550.0,
            ),
        ]

        page = _make_ordered_page(1, regions)
        ordered_cir = OrderedLayoutCIR(
            document_id="doc_suzuki_f8d_overhaul",
            total_pages=1,
            pages=(page,),
            ordered_regions=page.ordered_regions,
            global_graph=page.reading_order_graph,
            provenance=_make_source_ref(1, 0, 800),
        )

        engine = AutomotiveProcedureEngine()
        proc_set = engine.reconstruct_procedures(ordered_cir)

        assert proc_set.total_procedures == 1
        proc = proc_set.procedures[0]
        assert proc.title == "Cylinder Head Disassembly & Overhaul"
        assert proc.category == ProcedureCategory.OVERHAUL
        assert len(proc.preconditions) >= 2
        assert len(proc.postconditions) >= 1

        # Check total steps
        assert proc.total_steps == 13  # 7 top level + 2 substeps in step 3 + 4 substeps in step 4

        # Validate SST extraction
        sst_tools = [t for t in proc.required_tools if t.is_sst]
        assert len(sst_tools) >= 1
        assert sst_tools[0].tool_number == "09916-14510"

        # Validate standard tools
        tool_names = [t.name.lower() for t in proc.required_tools]
        assert "micrometer" in tool_names

        # Validate mandatory replacement consumables
        mat_names = [m.name.lower() for m in proc.required_materials if m.is_replacement_mandatory]
        assert any("valve stem seal" in m or "stem seal" in m for m in mat_names)
        assert any("gasket" in m for m in mat_names)

        # Validate warning binding
        first_step = proc.steps[0]
        assert len(first_step.bound_admonitions) >= 1
        assert first_step.bound_admonitions[0].admonition_type == AdmonitionType.WARNING

        # Validate cross-reference
        step_6 = [s for s in proc.steps if "micrometer" in s.action_text.lower()][0]
        assert "Table 6A-2" in step_6.referenced_tables or any("6A-2" in t for t in step_6.referenced_tables)


class TestMarutiSuzukiK10BManualProcedures:
    """Test suite validating against Maruti Suzuki K10B Engine Manual procedures."""

    def test_timing_chain_oil_pump_removal(self) -> None:
        regions = [
            _make_ordered_region(
                "h_k10b_01",
                "Timing Chain and Oil Pump Removal",
                RegionType.HEADING,
                page=2,
                order_idx=1,
                top=50.0,
                bottom=70.0,
            ),
            _make_ordered_region(
                "pre_k10b_01",
                "Prior to removal:\nDisconnect negative (-) cable from battery.\nDrain engine oil.",
                RegionType.BODY,
                page=2,
                order_idx=2,
                top=75.0,
                bottom=110.0,
            ),
            _make_ordered_region(
                "caution_k10b_01",
                "CAUTION: Do not rotate crankshaft after timing chain removal to prevent valve collision.",
                RegionType.WARNING_BOX,
                page=2,
                order_idx=3,
                top=115.0,
                bottom=145.0,
            ),
            _make_ordered_region(
                "steps_k10b_01",
                "1. Remove oil filter using SST 09915-64510 (Oil filter wrench).\n"
                "2. Remove water pump pulley and crankshaft pulley bolt.\n"
                "3. Remove timing chain cover by loosening 14 securing bolts [A] as shown in Fig. 6A-8.\n"
                "4. Apply Suzuki Bond 1215 to sealing surfaces upon installation.\n"
                "5. Install crankshaft oil seal using SST 09913-75810 (Oil seal installer).",
                RegionType.LIST,
                page=2,
                order_idx=4,
                top=150.0,
                bottom=400.0,
            ),
        ]

        page = _make_ordered_page(2, regions)
        ordered_cir = OrderedLayoutCIR(
            document_id="doc_maruti_k10b",
            total_pages=1,
            pages=(page,),
            ordered_regions=page.ordered_regions,
            global_graph=page.reading_order_graph,
            provenance=_make_source_ref(2, 0, 800),
        )

        engine = AutomotiveProcedureEngine()
        proc_set = engine.reconstruct_procedures(ordered_cir)

        assert proc_set.total_procedures == 1
        proc = proc_set.procedures[0]
        assert proc.title == "Timing Chain and Oil Pump Removal"
        assert proc.category == ProcedureCategory.REMOVAL_DISASSEMBLY
        assert len(proc.steps) == 5

        # Check SSTs
        sst_nums = [t.tool_number for t in proc.required_tools if t.is_sst]
        assert "09915-64510" in sst_nums
        assert "09913-75810" in sst_nums

        # Check Material
        mat_names = [m.name.lower() for m in proc.required_materials]
        assert any("suzuki bond" in m for m in mat_names)

        # Check Figure and Callout references
        step_3 = proc.steps[2]
        assert "Fig. 6A-8" in step_3.referenced_figures
        assert "A" in step_3.referenced_callouts


class TestMultiPageProcedureContinuation:
    """Test multi-page procedure continuation stitching across page breaks."""

    def test_multi_page_procedure_stitching(self) -> None:
        # Page 1: Steps 1 to 3
        p1_regions = [
            _make_ordered_region("h_p1", "Piston and Connecting Rod Assembly", RegionType.HEADING, 1, 1, 50, 70),
            _make_ordered_region(
                "steps_p1",
                "1. Apply clean engine oil to piston pin and connecting rod small end.\n"
                "2. Install piston rings using piston ring expander.\n"
                "3. Position piston ring gaps at 120-degree intervals as shown in Fig. 6A-15.",
                RegionType.LIST,
                1,
                2,
                75,
                250,
            ),
        ]
        page1 = _make_ordered_page(1, p1_regions)

        # Page 2: Steps 4 to 6 with (Continued) title
        p2_regions = [
            _make_ordered_region("h_p2", "Piston and Connecting Rod Assembly (Continued)", RegionType.HEADING, 2, 1, 50, 70),
            _make_ordered_region(
                "steps_p2",
                "4. Compress piston rings using piston ring compressor.\n"
                "5. Insert piston into cylinder bore matching front arrow mark toward timing chain side.\n"
                "6. Torque connecting rod cap nuts to specification. Refer to Table 6A-1.",
                RegionType.LIST,
                2,
                2,
                75,
                250,
            ),
        ]
        page2 = _make_ordered_page(2, p2_regions)

        ordered_cir = OrderedLayoutCIR(
            document_id="doc_multi_page_piston",
            total_pages=2,
            pages=(page1, page2),
            ordered_regions=page1.ordered_regions + page2.ordered_regions,
            global_graph=page1.reading_order_graph,
            provenance=_make_source_ref(1, 0, 800),
        )

        engine = AutomotiveProcedureEngine()
        proc_set = engine.reconstruct_procedures(ordered_cir)

        # Multi-page procedure should be stitched into exactly 1 procedure
        assert proc_set.total_procedures == 1
        proc = proc_set.procedures[0]
        assert proc.title == "Piston and Connecting Rod Assembly"
        assert proc.is_multi_page is True
        assert proc.page_span == (1, 2)
        assert len(proc.steps) == 6

        # Check sequence monotonicity across the stitched pages
        for idx, step in enumerate(proc.steps, start=1):
            assert step.sequence_number == idx

        # Page 1 steps have page_number=1, Page 2 steps have page_number=2
        assert proc.steps[0].page_number == 1
        assert proc.steps[5].page_number == 2
