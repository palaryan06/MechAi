"""Linker for binding diagrams to tables."""

from __future__ import annotations

import re

from mechai.contracts.diagrams import DiagramFigure, DiagramLabel
from mechai.contracts.tables import AutomotiveTableSet


class TableLinker:
    """Links diagrams to tables based on explicit references."""

    def __init__(self) -> None:
        """Initialize the table linker."""
        self._table_ref_pattern = re.compile(r"Table\s*([A-Z0-9\-]+)", re.IGNORECASE)

    def link_tables(
        self,
        figure: DiagramFigure | None,
        labels: tuple[DiagramLabel, ...],
        table_set: AutomotiveTableSet | None,
    ) -> list[str]:
        """Find table IDs referenced by this diagram."""
        if not table_set:
            return []

        linked_ids: set[str] = set()
        
        # Collect all text from figure title and labels
        texts_to_check = []
        if figure:
            texts_to_check.append(figure.title)
        for label in labels:
            texts_to_check.append(label.text)
            
        for text in texts_to_check:
            for match in self._table_ref_pattern.finditer(text):
                table_ident = f"TABLE {match.group(1).upper()}"
                # Find matching table
                for table in table_set.tables:
                    if table.title and table_ident in table.title.upper():
                        linked_ids.add(table.table_id)
                        
        return sorted(list(linked_ids))
