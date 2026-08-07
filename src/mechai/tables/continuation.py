"""Multi-Page Table Continuation Detector and Stitcher (RFC-AUTO-001).

Deterministically detects and merges tables that span across page boundaries in OEM manuals,
matching repeated headers, '(Continued)' markers, and column geometries while preserving
per-cell page numbers and spatial grounding provenance.
"""

from __future__ import annotations

import re

from mechai.contracts.tables import AutomotiveTable, AutomotiveTableRow
from mechai.tables.config import TableEngineConfig

_CONTINUATION_TITLE_RE = re.compile(
    r"""(?xi)
    (?:
        \(cont(?:inued|\'d)?\)|
        cont(?:inued|\'d)|
        \(continued\s+from\s+page\s+\d+\)
    )
    """
)


class AutomotiveTableContinuationStitcher:
    """Deterministic stitcher for multi-page continuation tables."""

    def __init__(self, config: TableEngineConfig | None = None) -> None:
        self.config = config or TableEngineConfig()

    def stitch_tables(self, tables: list[AutomotiveTable]) -> tuple[AutomotiveTable, ...]:
        """Detect continuation pairs across consecutive pages and stitch them into unified tables."""
        if len(tables) <= 1:
            return tuple(tables)

        # Sort tables by (page_number, bbox.top)
        sorted_tables = sorted(tables, key=lambda t: (t.page_number, t.bbox.top))
        stitched: list[AutomotiveTable] = []
        skip_indices: set[int] = set()

        for i, table_a in enumerate(sorted_tables):
            if i in skip_indices:
                continue

            current_table = table_a
            chain: list[AutomotiveTable] = [current_table]

            for j in range(i + 1, len(sorted_tables)):
                if j in skip_indices:
                    continue

                candidate = sorted_tables[j]

                # Check if candidate is a continuation of current_table
                if self._is_continuation(current_table, candidate):
                    chain.append(candidate)
                    skip_indices.add(j)
                    current_table = candidate
                elif candidate.page_number > current_table.page_number + self.config.max_continuation_page_gap:
                    # Page gap exceeded
                    break

            if len(chain) == 1:
                stitched.append(chain[0])
            else:
                # Merge chain into single multi-page table
                merged_table = self._merge_table_chain(chain)
                stitched.append(merged_table)

        return tuple(stitched)

    def _is_continuation(self, table_a: AutomotiveTable, table_b: AutomotiveTable) -> bool:
        """Evaluate whether table_b is a continuation of table_a on a subsequent page."""
        # 1. Page constraint: must be on subsequent page within allowed gap
        page_diff = table_b.page_number - table_a.page_number
        if page_diff < 1 or page_diff > self.config.max_continuation_page_gap:
            return False

        # 2. Column count must match
        if table_a.num_columns != table_b.num_columns or table_a.num_columns == 0:
            return False

        # 3. Explicit Title Continuation marker
        title_b = table_b.title or ""
        if _CONTINUATION_TITLE_RE.search(title_b):
            return True

        # 4. Header Jaccard similarity check
        headers_a = set(n.lower().strip() for n in table_a.header.flat_column_names if n.strip())
        headers_b = set(n.lower().strip() for n in table_b.header.flat_column_names if n.strip())

        if headers_a and headers_b:
            intersection = len(headers_a.intersection(headers_b))
            union = len(headers_a.union(headers_b))
            similarity = intersection / union if union > 0 else 0.0

            if similarity >= self.config.header_similarity_threshold:
                # Table types should match
                return table_a.table_type == table_b.table_type

        return False

    def _merge_table_chain(self, chain: list[AutomotiveTable]) -> AutomotiveTable:
        """Merge a sequence of continuation tables into a single unified AutomotiveTable."""
        base = chain[0]
        all_rows: list[AutomotiveTableRow] = list(base.rows)
        row_counter = len(all_rows)

        all_page_numbers: list[int] = list(base.page_span or (base.page_number,))
        all_notes: list[str] = list(base.notes)
        all_warnings: list[str] = list(base.warnings)
        all_footnotes = list(base.footnotes)
        all_source_region_ids: list[str] = list(base.source_region_ids)

        for cont_table in chain[1:]:
            all_page_numbers.extend(cont_table.page_span or (cont_table.page_number,))
            all_notes.extend(cont_table.notes)
            all_warnings.extend(cont_table.warnings)
            all_footnotes.extend(cont_table.footnotes)
            all_source_region_ids.extend(cont_table.source_region_ids)

            # Re-index data rows from continuation table
            for row in cont_table.rows:
                # Update cell row_index
                updated_cells = tuple(
                    c.model_copy(update={"row_index": row_counter})
                    for c in row.cells
                )
                updated_row = row.model_copy(
                    update={
                        "row_index": row_counter,
                        "cells": updated_cells,
                    }
                )
                all_rows.append(updated_row)
                row_counter += 1

        # Deduplicate page span preserving order
        unique_pages = tuple(dict.fromkeys(all_page_numbers))
        unique_footnotes = tuple(dict.fromkeys(all_footnotes))
        unique_notes = tuple(dict.fromkeys(all_notes))
        unique_warnings = tuple(dict.fromkeys(all_warnings))

        return base.model_copy(
            update={
                "rows": tuple(all_rows),
                "num_rows": len(all_rows),
                "is_multi_page": True,
                "page_span": unique_pages,
                "notes": unique_notes,
                "warnings": unique_warnings,
                "footnotes": unique_footnotes,
                "source_region_ids": tuple(dict.fromkeys(all_source_region_ids)),
            }
        )
