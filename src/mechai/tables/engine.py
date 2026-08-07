"""Automotive Table Intelligence Engine (RFC-AUTO-001).

Transforms OrderedLayoutCIR into richly structured AutomotiveTableSet models with deterministic
reconstruction, semantic classification, unit normalization, footnote resolution,
and multi-page continuation stitching.
"""

from __future__ import annotations

from collections.abc import Iterator

from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import (
    OrderedLayoutCIR,
    OrderedLayoutRegion,
    OrderedPageCIR,
)
from mechai.contracts.provenance import ExtractionMethod, SourceRef
from mechai.contracts.tables import (
    AutomotiveTable,
    AutomotiveTableEngineProtocol,
    AutomotiveTableFootnote,
    AutomotiveTableSet,
)
from mechai.tables.classifier import AutomotiveTableClassifier
from mechai.tables.config import TableEngineConfig
from mechai.tables.continuation import AutomotiveTableContinuationStitcher
from mechai.tables.footnote_extractor import AutomotiveFootnoteExtractor
from mechai.tables.grid_reconstructor import SpatialGridReconstructor


class AutomotiveTableEngine(AutomotiveTableEngineProtocol):
    """Stage 6 Automotive Table Intelligence Engine."""

    def __init__(self, config: TableEngineConfig | None = None) -> None:
        self.config = config or TableEngineConfig()
        self.grid_reconstructor = SpatialGridReconstructor(self.config)
        self.stitcher = AutomotiveTableContinuationStitcher(self.config)

    def reconstruct_tables(self, ordered_layout: OrderedLayoutCIR) -> AutomotiveTableSet:
        """Process entire OrderedLayoutCIR and produce complete AutomotiveTableSet."""
        all_tables: list[AutomotiveTable] = []

        for page in ordered_layout.pages:
            page_tables = self.reconstruct_page_tables(page)
            all_tables.extend(page_tables)

        # Multi-page continuation stitching
        stitched_tables = self.stitcher.stitch_tables(all_tables)

        return AutomotiveTableSet(
            document_id=ordered_layout.document_id,
            tables=stitched_tables,
            total_tables=len(stitched_tables),
            provenance=SourceRef(
                page_number=1,
                extraction_method=ExtractionMethod.RULE,
                confidence=1.0,
            ),
        )

    def reconstruct_page_tables(self, ordered_page: OrderedPageCIR) -> tuple[AutomotiveTable, ...]:
        """Extract and reconstruct all automotive tables on a single page."""
        tables: list[AutomotiveTable] = []
        regions = ordered_page.ordered_regions

        for idx, reg in enumerate(regions):
            if reg.region_type != RegionType.TABLE_REGION:
                continue

            # 1. Harvest preceding Title or Caption
            table_title = self._find_preceding_title(regions, idx)

            # 2. Harvest trailing Notes and Warnings
            notes, warnings, footnote_defs = self._harvest_trailing_annotations(regions, idx, ordered_page.page_number)

            # 3. Spatial Grid Reconstruction
            header, rows, num_rows, num_cols = self.grid_reconstructor.reconstruct_grid(reg)

            # 4. Extract sample cell texts for semantic classification
            sample_cells = [
                cell.raw_text
                for row in rows
                for cell in row.cells
            ]

            # 5. Typographic & Semantic Table Classification
            table_type = AutomotiveTableClassifier.classify(
                title=table_title,
                header_names=header.flat_column_names,
                sample_cells=sample_cells,
            )

            # 6. Construct AutomotiveTable
            table_id = f"table_p{ordered_page.page_number}_{len(tables) + 1:03d}"
            table = AutomotiveTable(
                table_id=table_id,
                title=table_title,
                table_type=table_type,
                confidence=reg.confidence,
                page_number=ordered_page.page_number,
                bbox=reg.bbox,
                header=header,
                rows=rows,
                num_rows=num_rows,
                num_columns=num_cols,
                notes=tuple(notes),
                warnings=tuple(warnings),
                footnotes=tuple(footnote_defs),
                is_multi_page=False,
                is_continuation=False,
                page_span=(ordered_page.page_number,),
                provenance=SourceRef(
                    page_number=ordered_page.page_number,
                    bbox=reg.bbox,
                    extraction_method=ExtractionMethod.RULE,
                    confidence=reg.confidence,
                ),
                source_region_ids=(reg.id,),
            )
            tables.append(table)

        return tuple(tables)

    def reconstruct_stream(self, ordered_pages: Iterator[OrderedPageCIR]) -> Iterator[AutomotiveTable]:
        """Stream reconstructed tables across pages sequentially."""
        for page in ordered_pages:
            page_tables = self.reconstruct_page_tables(page)
            for tbl in page_tables:
                yield tbl

    def _find_preceding_title(self, regions: tuple[OrderedLayoutRegion, ...], table_idx: int) -> str | None:
        """Find immediate heading or caption preceding a table."""
        if table_idx > 0:
            prev_reg = regions[table_idx - 1]
            if prev_reg.region_type in (RegionType.HEADING, RegionType.TITLE, RegionType.CAPTION):
                # Check spatial vertical distance (< 40 pt)
                curr_table_bbox = regions[table_idx].bbox
                if curr_table_bbox.top - prev_reg.bbox.bottom <= 40.0:
                    return prev_reg.text.strip()
        return None

    def _harvest_trailing_annotations(
        self,
        regions: tuple[OrderedLayoutRegion, ...],
        table_idx: int,
        page_number: int,
    ) -> tuple[list[str], list[str], list[AutomotiveTableFootnote]]:
        """Harvest immediately trailing note boxes, warning boxes, and footnote definitions."""
        notes: list[str] = []
        warnings: list[str] = []
        footnotes: list[AutomotiveTableFootnote] = []

        curr_table_bbox = regions[table_idx].bbox
        lookahead_idx = table_idx + 1

        while lookahead_idx < len(regions):
            next_reg = regions[lookahead_idx]
            # Must be within 30 pt below
            if next_reg.bbox.top - curr_table_bbox.bottom > 35.0:
                break

            if next_reg.region_type == RegionType.NOTE_BOX:
                notes.append(next_reg.text.strip())
                # Check if note text contains footnote definitions
                fn_list = AutomotiveFootnoteExtractor.parse_footnote_lines(
                    lines=next_reg.text.splitlines(),
                    page_number=page_number,
                    provenance=SourceRef(
                        page_number=page_number,
                        bbox=next_reg.bbox,
                        extraction_method=ExtractionMethod.RULE,
                        confidence=next_reg.confidence,
                    ),
                )
                footnotes.extend(fn_list)
            elif next_reg.region_type == RegionType.WARNING_BOX:
                warnings.append(next_reg.text.strip())
            else:
                break

            lookahead_idx += 1

        return notes, warnings, footnotes
