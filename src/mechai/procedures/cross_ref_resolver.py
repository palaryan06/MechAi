"""Cross-Reference Resolver for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Deterministically extracts and resolves references in step text to tables (in AutomotiveTableSet),
figures/diagrams, exploded view callout markers, and page numbers.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mechai.procedures.config import ProcedureEngineConfig

if TYPE_CHECKING:
    from mechai.contracts.tables import AutomotiveTableSet


class CrossReferenceResolver:
    """Deterministic resolver for cross-references to tables, figures, callouts, and pages."""

    def __init__(self, config: ProcedureEngineConfig | None = None) -> None:
        self._config = config or ProcedureEngineConfig()
        self._re_table = re.compile(self._config.table_ref_regex, re.IGNORECASE)
        self._re_figure = re.compile(self._config.figure_ref_regex, re.IGNORECASE)
        self._re_callout = re.compile(self._config.callout_ref_regex)
        self._re_page = re.compile(self._config.page_ref_regex, re.IGNORECASE)

    def resolve_references(
        self,
        text: str,
        table_set: AutomotiveTableSet | None = None,
    ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[int, ...]]:
        """Resolve (referenced_tables, referenced_figures, referenced_callouts, referenced_pages)."""
        tables: list[str] = []
        figures: list[str] = []
        callouts: list[str] = []
        pages: list[int] = []

        # 1. Table references
        for m in self._re_table.finditer(text):
            tbl_match_str = m.group(0).strip()
            table_id: str | None = None

            # Attempt matching against existing table set
            if table_set is not None:
                for tbl in table_set.tables:
                    if tbl.title and tbl.title.lower() in tbl_match_str.lower():
                        table_id = tbl.table_id
                        break
                    if m.group(1) and m.group(1) in tbl.table_id:
                        table_id = tbl.table_id
                        break

            if table_id:
                if table_id not in tables:
                    tables.append(table_id)
            else:
                if tbl_match_str not in tables:
                    tables.append(tbl_match_str)

        # 2. Figure references
        for m in self._re_figure.finditer(text):
            fig_str = m.group(0).strip()
            if fig_str not in figures:
                figures.append(fig_str)

        # 3. Callout markers e.g. [A], (1)
        for m in self._re_callout.finditer(text):
            callout = m.group(1) or m.group(2)
            if callout and callout not in callouts:
                callouts.append(callout)

        # 4. Page references
        for m in self._re_page.finditer(text):
            page_str = m.group(1).strip()
            # If plain integer
            if page_str.isdigit():
                p_num = int(page_str)
                if p_num not in pages:
                    pages.append(p_num)

        return (
            tuple(tables),
            tuple(figures),
            tuple(callouts),
            tuple(pages),
        )
