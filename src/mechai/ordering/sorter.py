"""Core Reading Order Engine and Spatial Sorter (Stage 2.1).

RFC-008: Deterministic horizontal band slicing, multi-column traversal,
figure-caption binding, callout priority insertion, and explainable graph
generation.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from mechai.contracts.layout import (
    ColumnGutter,
    LayoutCIR,
    LayoutRegion,
    PageLayoutCIR,
    RegionType,
)
from mechai.contracts.ordering import (
    AlternativeReadingPath,
    FlowEdgeType,
    OrderedLayoutCIR,
    OrderedLayoutRegion,
    OrderedPageCIR,
    ReadingFlowType,
    ReadingOrderEngineProtocol,
    ReadingOrderEvidence,
    ReadingOrderNode,
)
from mechai.contracts.provenance import SourceRef
from mechai.ordering.config import ReadingOrderConfig
from mechai.ordering.graph import ReadingOrderGraphBuilder

if TYPE_CHECKING:
    from collections.abc import Iterator


class ReadingOrderEngine(ReadingOrderEngineProtocol):
    """Stage 2.1 Engine: Determines human reading order and generates ReadingOrderGraphs."""

    def __init__(self, config: ReadingOrderConfig | None = None) -> None:
        self.config = config or ReadingOrderConfig()

    def process(self, layout: LayoutCIR) -> OrderedLayoutCIR:
        """Universal entry point conforming to OrderedLayoutEngineProtocol."""
        return self.order_layout(layout)

    def order_layout(self, layout: LayoutCIR) -> OrderedLayoutCIR:
        """Process an entire LayoutCIR and return OrderedLayoutCIR with global graphs."""
        ordered_pages: list[OrderedPageCIR] = []
        all_ordered_regions: list[OrderedLayoutRegion] = []
        global_builder = ReadingOrderGraphBuilder()

        prev_exit_id: str | None = None
        global_rank = 1

        for page in layout.pages:
            ordered_page = self.order_page(page, prev_page_exit_id=prev_exit_id)
            ordered_pages.append(ordered_page)

            # Accumulate global graph nodes and edges
            for node in ordered_page.reading_order_graph.nodes:
                global_builder.add_node(node)

            for edge in ordered_page.reading_order_graph.edges:
                global_builder.add_edge(
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    edge_type=edge.edge_type,
                    confidence=edge.confidence,
                    evidence=edge.evidence,
                )

            for alt in ordered_page.alternative_paths:
                global_builder.add_alternative_path(alt)

            # Re-index global ordered regions
            for reg in ordered_page.ordered_regions:
                enriched = OrderedLayoutRegion(
                    id=reg.id,
                    bbox=reg.bbox,
                    page_number=reg.page_number,
                    region_type=reg.region_type,
                    confidence=reg.confidence,
                    provenance=reg.provenance,
                    text=reg.text,
                    reading_zone_id=reg.reading_zone_id,
                    column_index=reg.column_index,
                    reading_order_index=global_rank,
                    reading_depth=reg.reading_depth,
                    is_primary_flow=reg.is_primary_flow,
                )
                all_ordered_regions.append(enriched)
                if reg.is_primary_flow:
                    global_rank += 1

            # Cross-page flow edge
            if self.config.cross_page_continuity and prev_exit_id and ordered_page.primary_sequence:
                next_entry_id = ordered_page.primary_sequence[0]
                prev_reg = next((r for r in all_ordered_regions if r.id == prev_exit_id), None)
                next_reg = next((r for r in all_ordered_regions if r.id == next_entry_id), None)
                if prev_reg and next_reg:
                    evidence = ReadingOrderEvidence(
                        decision_rule="cross_page_continuation",
                        source_zone=prev_reg.reading_zone_id or "body",
                        target_zone=next_reg.reading_zone_id or "body",
                        spatial_distance_pt=0.0,
                        confidence=0.90,
                        rationale=(
                            f"Cross-page flow from page {prev_reg.page_number} "
                            f"to {next_reg.page_number}"
                        ),
                    )
                    global_builder.add_edge(
                        source_id=prev_exit_id,
                        target_id=next_entry_id,
                        edge_type=FlowEdgeType.CROSS_PAGE_FLOW,
                        confidence=0.90,
                        evidence=evidence,
                    )

            if ordered_page.primary_sequence:
                prev_exit_id = ordered_page.primary_sequence[-1]

        # Finalize global primary path
        global_primary_path: list[str] = []
        for p in ordered_pages:
            global_primary_path.extend(p.primary_sequence)
        global_builder.set_primary_path(global_primary_path)

        global_graph = global_builder.build()

        return OrderedLayoutCIR(
            document_id=layout.document_id,
            source_path=layout.source_path,
            total_pages=layout.total_pages,
            pages=tuple(ordered_pages),
            ordered_regions=tuple(all_ordered_regions),
            global_graph=global_graph,
            provenance=layout.provenance or SourceRef(page_number=1, confidence=1.0),
        )

    def order_stream(self, layout: LayoutCIR) -> Iterator[OrderedPageCIR]:
        """Stream ordered page representations sequentially for memory efficiency."""
        prev_exit_id: str | None = None
        for page in layout.pages:
            ordered_page = self.order_page(page, prev_page_exit_id=prev_exit_id)
            if ordered_page.primary_sequence:
                prev_exit_id = ordered_page.primary_sequence[-1]
            yield ordered_page

    def order_page(
        self,
        page_layout: PageLayoutCIR,
        prev_page_exit_id: str | None = None,
    ) -> OrderedPageCIR:
        """Determine deterministic human reading order for a single PageLayoutCIR."""
        if not page_layout.regions:
            # Empty page handling
            empty_graph = ReadingOrderGraphBuilder().build()
            return OrderedPageCIR(
                page_number=page_layout.page_number,
                width=page_layout.width,
                height=page_layout.height,
                margins=page_layout.margins,
                header_zone=page_layout.header_zone,
                footer_zone=page_layout.footer_zone,
                columns=page_layout.columns,
                ordered_regions=(),
                reading_order_graph=empty_graph,
                primary_sequence=(),
                alternative_paths=(),
                sequence_confidence=1.0,
                reading_flow_type=ReadingFlowType.SINGLE_COLUMN,
            )

        builder = ReadingOrderGraphBuilder()

        # 1. Separate headers, footers, sidebars, and body regions
        headers: list[LayoutRegion] = []
        footers: list[LayoutRegion] = []
        sidebars: list[LayoutRegion] = []
        body_regions: list[LayoutRegion] = []

        for reg in page_layout.regions:
            if reg.region_type == RegionType.HEADER or reg.reading_zone_id == "zone_header":
                headers.append(reg)
            elif reg.region_type == RegionType.FOOTER or reg.reading_zone_id == "zone_footer":
                footers.append(reg)
            elif reg.region_type == RegionType.SIDEBAR or reg.reading_zone_id == "zone_sidebar":
                sidebars.append(reg)
            else:
                body_regions.append(reg)

        # 2. Bind Captions to FigureRegion / TableRegion
        captions = [r for r in body_regions if r.region_type == RegionType.CAPTION]
        visual_targets = [
            r
            for r in body_regions
            if r.region_type in (RegionType.FIGURE_REGION, RegionType.TABLE_REGION)
        ]
        caption_pairs: dict[str, str] = {}  # target_id -> caption_id
        paired_caption_ids: set[str] = set()

        for cap in captions:
            best_target: LayoutRegion | None = None
            min_dist = float("inf")
            for target in visual_targets:
                # Vertical gap check: caption usually below target or immediately above
                v_dist = min(
                    abs(cap.bbox.top - target.bbox.bottom),
                    abs(target.bbox.top - cap.bbox.bottom),
                )
                # Horizontal overlap check
                h_overlap = max(
                    0.0,
                    min(cap.bbox.right, target.bbox.right) - max(cap.bbox.left, target.bbox.left),
                )
                if v_dist <= self.config.caption_max_distance_pt and (
                    h_overlap > 0.0 or abs(cap.bbox.center_x - target.bbox.center_x) < 50.0
                ):
                    if v_dist < min_dist:
                        min_dist = v_dist
                        best_target = target

            if best_target and best_target.id not in caption_pairs:
                caption_pairs[best_target.id] = cap.id
                paired_caption_ids.add(cap.id)

        # 3. Horizontal Band Slicing for Body Elements
        bands = self._slice_into_horizontal_bands(
            body_regions=body_regions,
            columns=page_layout.columns,
            page_width=page_layout.width,
            paired_caption_ids=paired_caption_ids,
        )

        # 4. Traverse Bands and build primary sequence & graph edges
        primary_ordered_regions: list[LayoutRegion] = []
        flow_edges_to_add: list[tuple[str, str, FlowEdgeType, float, ReadingOrderEvidence]] = []

        last_node_id: str | None = None

        for band in bands:
            band_ordered = self._order_band(
                band=band,
                columns=page_layout.columns,
                caption_pairs=caption_pairs,
                body_regions_map={r.id: r for r in body_regions},
            )

            for _idx, reg in enumerate(band_ordered):
                primary_ordered_regions.append(reg)

                if last_node_id is not None:
                    # Determine transition type and rationale
                    prev_reg = next(r for r in body_regions if r.id == last_node_id)
                    edge_type, rule, rationale, dist = self._classify_edge_transition(
                        prev_reg=prev_reg,
                        curr_reg=reg,
                        columns=page_layout.columns,
                        caption_pairs=caption_pairs,
                    )
                    evidence = ReadingOrderEvidence(
                        decision_rule=rule,
                        source_zone=prev_reg.reading_zone_id or "body",
                        target_zone=reg.reading_zone_id or "body",
                        spatial_distance_pt=dist,
                        confidence=0.92,
                        rationale=rationale,
                    )
                    flow_edges_to_add.append((last_node_id, reg.id, edge_type, 0.92, evidence))

                last_node_id = reg.id

        # 5. Connect Cross-Page edge if prev_page_exit_id provided
        if prev_page_exit_id and primary_ordered_regions and self.config.cross_page_continuity:
            first_reg = primary_ordered_regions[0]
            evidence = ReadingOrderEvidence(
                decision_rule="cross_page_flow",
                source_zone="previous_page_exit",
                target_zone=first_reg.reading_zone_id or "body",
                spatial_distance_pt=0.0,
                confidence=0.90,
                rationale=f"Sequential cross-page flow to page {page_layout.page_number}",
            )
            flow_edges_to_add.append(
                (prev_page_exit_id, first_reg.id, FlowEdgeType.CROSS_PAGE_FLOW, 0.90, evidence)
            )

        # 6. Build Alternative Paths for Sidebars
        alt_paths: list[AlternativeReadingPath] = []
        if sidebars and primary_ordered_regions:
            sidebar_regions_sorted = sorted(sidebars, key=lambda r: r.bbox.top)
            first_body_id = primary_ordered_regions[0].id
            last_body_id = primary_ordered_regions[-1].id

            alt_path = AlternativeReadingPath(
                path_id=f"alt_sidebar_p{page_layout.page_number}",
                name="Sidebar Exploration Path",
                description="Alternative branch to read marginal sidebar annotations",
                branch_source_id=first_body_id,
                rejoin_target_id=last_body_id,
                region_ids=tuple(r.id for r in sidebar_regions_sorted),
                confidence=0.85,
            )
            alt_paths.append(alt_path)

            # Add sidebar branch edge
            for s_reg in sidebar_regions_sorted:
                evidence = ReadingOrderEvidence(
                    decision_rule="sidebar_branching",
                    source_zone="zone_body",
                    target_zone=s_reg.reading_zone_id or "zone_sidebar",
                    spatial_distance_pt=abs(
                        s_reg.bbox.left - primary_ordered_regions[0].bbox.right
                    ),
                    confidence=0.85,
                    rationale="Branching into marginal sidebar annotation",
                )
                flow_edges_to_add.append(
                    (first_body_id, s_reg.id, FlowEdgeType.SIDEBAR_BRANCH, 0.85, evidence)
                )

        # 7. Add Header / Footer Attachments
        if headers and primary_ordered_regions:
            first_body_id = primary_ordered_regions[0].id
            for h in headers:
                evidence = ReadingOrderEvidence(
                    decision_rule="header_attachment",
                    source_zone=h.reading_zone_id or "zone_header",
                    target_zone="zone_body",
                    spatial_distance_pt=max(
                        0.0, primary_ordered_regions[0].bbox.top - h.bbox.bottom
                    ),
                    confidence=0.95,
                    rationale="Logical attachment of running header outside linear body narrative",
                )
                flow_edges_to_add.append(
                    (h.id, first_body_id, FlowEdgeType.HEADER_ATTACHMENT, 0.95, evidence)
                )

        if footers and primary_ordered_regions:
            last_body_id = primary_ordered_regions[-1].id
            for f in footers:
                evidence = ReadingOrderEvidence(
                    decision_rule="footer_attachment",
                    source_zone="zone_body",
                    target_zone=f.reading_zone_id or "zone_footer",
                    spatial_distance_pt=max(
                        0.0, f.bbox.top - primary_ordered_regions[-1].bbox.bottom
                    ),
                    confidence=0.95,
                    rationale="Logical attachment of running footer outside linear body narrative",
                )
                flow_edges_to_add.append(
                    (last_body_id, f.id, FlowEdgeType.FOOTER_ATTACHMENT, 0.95, evidence)
                )

        # 8. Assemble all OrderedLayoutRegions
        final_ordered_regions: list[OrderedLayoutRegion] = []
        primary_sequence = tuple(r.id for r in primary_ordered_regions)
        order_rank = 1

        # Primary body regions
        for reg in primary_ordered_regions:
            depth = (
                1
                if reg.region_type
                in (RegionType.WARNING_BOX, RegionType.NOTE_BOX, RegionType.CAPTION)
                else 0
            )
            ordered_reg = OrderedLayoutRegion(
                id=reg.id,
                bbox=reg.bbox,
                page_number=reg.page_number,
                region_type=reg.region_type,
                confidence=reg.confidence,
                provenance=reg.provenance,
                text=reg.text,
                reading_zone_id=reg.reading_zone_id,
                column_index=reg.column_index,
                reading_order_index=order_rank,
                reading_depth=depth,
                is_primary_flow=True,
            )
            final_ordered_regions.append(ordered_reg)
            order_rank += 1

            # Add node to graph builder
            builder.add_node(
                ReadingOrderNode(
                    region_id=reg.id,
                    page_number=reg.page_number,
                    region_type=reg.region_type,
                    reading_zone_id=reg.reading_zone_id,
                    column_index=reg.column_index,
                    bbox=reg.bbox,
                    order_index=order_rank - 1,
                    is_primary_flow=True,
                )
            )

        # Non-primary regions (Headers, Footers, Sidebars)
        for non_primary_list, depth_val in [(headers, 0), (sidebars, 1), (footers, 0)]:
            for reg in non_primary_list:
                ordered_reg = OrderedLayoutRegion(
                    id=reg.id,
                    bbox=reg.bbox,
                    page_number=reg.page_number,
                    region_type=reg.region_type,
                    confidence=reg.confidence,
                    provenance=reg.provenance,
                    text=reg.text,
                    reading_zone_id=reg.reading_zone_id,
                    column_index=reg.column_index,
                    reading_order_index=order_rank,
                    reading_depth=depth_val,
                    is_primary_flow=False,
                )
                final_ordered_regions.append(ordered_reg)
                order_rank += 1

                builder.add_node(
                    ReadingOrderNode(
                        region_id=reg.id,
                        page_number=reg.page_number,
                        region_type=reg.region_type,
                        reading_zone_id=reg.reading_zone_id,
                        column_index=reg.column_index,
                        bbox=reg.bbox,
                        order_index=order_rank - 1,
                        is_primary_flow=False,
                    )
                )

        # Add edges and paths
        for src, dst, etype, conf, evid in flow_edges_to_add:
            builder.add_edge(src, dst, etype, conf, evid)

        builder.set_primary_path(primary_sequence)
        for alt in alt_paths:
            builder.add_alternative_path(alt)

        page_graph = builder.build()
        flow_type = self._determine_reading_flow_type(
            columns=page_layout.columns,
            bands=bands,
            has_sidebars=bool(sidebars),
        )
        seq_conf = builder.compute_sequence_confidence()

        return OrderedPageCIR(
            page_number=page_layout.page_number,
            width=page_layout.width,
            height=page_layout.height,
            margins=page_layout.margins,
            header_zone=page_layout.header_zone,
            footer_zone=page_layout.footer_zone,
            columns=page_layout.columns,
            ordered_regions=tuple(final_ordered_regions),
            reading_order_graph=page_graph,
            primary_sequence=primary_sequence,
            alternative_paths=tuple(alt_paths),
            sequence_confidence=seq_conf,
            reading_flow_type=flow_type,
        )

    def _slice_into_horizontal_bands(
        self,
        body_regions: list[LayoutRegion],
        columns: tuple[ColumnGutter, ...],
        page_width: float,
        paired_caption_ids: set[str],
    ) -> list[list[LayoutRegion]]:
        """Slice page elements into vertical bands of Spanning elements vs Multi-Column Blocks."""
        if not body_regions:
            return []

        if not columns:
            # Single-column page: single band sorted top-to-bottom
            return [sorted(body_regions, key=lambda r: r.bbox.top)]

        # Classify which regions are "spanning" across column gutters
        def is_spanning(r: LayoutRegion) -> bool:
            if r.id in paired_caption_ids:
                return False  # Captions travel with their visual targets
            if r.reading_zone_id == "zone_body_span":
                return True
            # Crosses a column gutter or is wider than 65% of page
            r_width = r.bbox.width
            if r_width > page_width * 0.65:
                return True
            for g in columns:
                if r.bbox.left < g.left and r.bbox.right > g.right:
                    return True
            return False

        # Sort all candidates by top coordinate
        sorted_all = sorted(body_regions, key=lambda r: r.bbox.top)
        bands: list[list[LayoutRegion]] = []
        current_multi_col_band: list[LayoutRegion] = []

        for reg in sorted_all:
            if reg.id in paired_caption_ids:
                # Paired captions are bound directly to their visual target in _order_band
                continue
            if is_spanning(reg):
                if current_multi_col_band:
                    bands.append(current_multi_col_band)
                    current_multi_col_band = []
                bands.append([reg])
            else:
                current_multi_col_band.append(reg)

        if current_multi_col_band:
            bands.append(current_multi_col_band)

        return bands

    def _order_band(
        self,
        band: list[LayoutRegion],
        columns: tuple[ColumnGutter, ...],
        caption_pairs: dict[str, str],
        body_regions_map: dict[str, LayoutRegion],
    ) -> list[LayoutRegion]:
        """Order elements inside a single band (column-by-column or single spanning block)."""
        if len(band) == 1:
            # Single spanning element
            target = band[0]
            ordered = [target]
            if target.id in caption_pairs:
                cap_id = caption_pairs[target.id]
                if cap_id in body_regions_map:
                    ordered.append(body_regions_map[cap_id])
            return ordered

        if not columns:
            # Single column band
            sorted_band = sorted(band, key=lambda r: r.bbox.top)
            return self._order_single_column_sequence(sorted_band, caption_pairs, body_regions_map)

        # Multi-column band: partition by column index
        col_buckets: dict[int, list[LayoutRegion]] = {}

        for reg in band:
            if reg.id in caption_pairs.values():
                # Will be inserted directly after its target
                continue

            c_idx = reg.column_index
            if c_idx is None:
                c_idx = self._resolve_column_index(reg, columns)

            if c_idx not in col_buckets:
                col_buckets[c_idx] = []
            col_buckets[c_idx].append(reg)

        # Sort columns from left to right (0, 1, 2, ...)
        ordered_band: list[LayoutRegion] = []
        for c_idx in sorted(col_buckets.keys()):
            col_regions = sorted(col_buckets[c_idx], key=lambda r: r.bbox.top)
            col_ordered = self._order_single_column_sequence(
                col_regions, caption_pairs, body_regions_map
            )
            ordered_band.extend(col_ordered)

        return ordered_band

    def _order_single_column_sequence(
        self,
        col_regions: list[LayoutRegion],
        caption_pairs: dict[str, str],
        body_regions_map: dict[str, LayoutRegion],
    ) -> list[LayoutRegion]:
        """Order elements in a single column, inserting captions immediately after targets."""
        ordered: list[LayoutRegion] = []
        for reg in col_regions:
            if reg.id in caption_pairs.values():
                continue
            ordered.append(reg)
            if reg.id in caption_pairs:
                cap_id = caption_pairs[reg.id]
                if cap_id in body_regions_map and body_regions_map[cap_id] not in ordered:
                    ordered.append(body_regions_map[cap_id])
        return ordered

    def _resolve_column_index(self, reg: LayoutRegion, columns: tuple[ColumnGutter, ...]) -> int:
        """Resolve 0-based column index based on region horizontal center relative to gutters."""
        if not columns:
            return 0
        cx = reg.bbox.center_x
        for idx, g in enumerate(columns):
            if cx < g.left:
                return idx
        return len(columns)

    def _classify_edge_transition(
        self,
        prev_reg: LayoutRegion,
        curr_reg: LayoutRegion,
        columns: tuple[ColumnGutter, ...],
        caption_pairs: dict[str, str],
    ) -> tuple[FlowEdgeType, str, str, float]:
        """Determine transition relationship and rationale between consecutive regions."""
        dist = math.sqrt(
            (curr_reg.bbox.center_x - prev_reg.bbox.center_x) ** 2
            + (curr_reg.bbox.center_y - prev_reg.bbox.center_y) ** 2
        )

        # Caption Link
        if caption_pairs.get(prev_reg.id) == curr_reg.id:
            return (
                FlowEdgeType.CAPTION_LINK,
                "caption_binding",
                f"Binding {prev_reg.region_type} to explanatory caption ({dist:.1f}pt)",
                dist,
            )

        # Warning / Note Box Priority
        if curr_reg.region_type in (RegionType.WARNING_BOX, RegionType.NOTE_BOX):
            return (
                FlowEdgeType.CALLOUT_ASIDE,
                "safety_callout_precedence",
                f"Prioritized safety callout {curr_reg.region_type} adjacent to procedural text",
                dist,
            )

        # Column Wrap
        prev_col = prev_reg.column_index
        curr_col = curr_reg.column_index
        if prev_col is not None and curr_col is not None and prev_col != curr_col:
            return (
                FlowEdgeType.COLUMN_WRAP,
                "multi_column_wrap",
                f"Column wrap from Column {prev_col} bottom to Column {curr_col} top",
                dist,
            )

        # Spanning Descent
        if prev_reg.reading_zone_id == "zone_body_span" or prev_reg.region_type in (
            RegionType.TITLE,
            RegionType.HEADING,
        ):
            if curr_reg.column_index == 0:
                return (
                    FlowEdgeType.SPANNING_DESCENT,
                    "spanning_band_descent",
                    f"Transition from spanning {prev_reg.region_type} into Column 0 below",
                    dist,
                )

        # Spanning Ascent
        if curr_reg.reading_zone_id == "zone_body_span" or curr_reg.region_type in (
            RegionType.TITLE,
            RegionType.HEADING,
            RegionType.TABLE_REGION,
        ):
            if prev_reg.column_index is not None and prev_reg.column_index > 0:
                return (
                    FlowEdgeType.SPANNING_ASCENT,
                    "spanning_band_ascent",
                    (
                        f"Transition from Column {prev_reg.column_index} "
                        f"into spanning {curr_reg.region_type}"
                    ),
                    dist,
                )

        # Natural Flow (Default)
        return (
            FlowEdgeType.NATURAL_FLOW,
            "vertical_natural_flow",
            f"Sequential top-to-bottom continuation in same reading zone ({dist:.1f}pt)",
            dist,
        )

    def _determine_reading_flow_type(
        self,
        columns: tuple[ColumnGutter, ...],
        bands: list[list[LayoutRegion]],
        has_sidebars: bool,
    ) -> ReadingFlowType:
        """Classify page reading flow topology."""
        if has_sidebars:
            return ReadingFlowType.SIDEBAR_INTERRUPTED

        if not columns or len(columns) == 0:
            return ReadingFlowType.SINGLE_COLUMN

        spanning_count = sum(1 for b in bands if len(b) == 1)
        multi_col_count = sum(1 for b in bands if len(b) > 1)

        if spanning_count > 0 and multi_col_count > 0:
            return ReadingFlowType.SPANNING_INTERLEAVED

        if multi_col_count > 0:
            return ReadingFlowType.MULTI_COLUMN_WRAP

        return ReadingFlowType.SINGLE_COLUMN
