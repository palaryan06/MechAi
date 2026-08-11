"""Linker for binding diagrams to procedures."""

from __future__ import annotations

from mechai.contracts.diagrams import DiagramFigure
from mechai.contracts.procedures import AutomotiveProcedureSet


class ProcedureLinker:
    """Links diagrams to procedures based on explicit references."""

    def link_procedures(
        self,
        figure: DiagramFigure | None,
        procedure_set: AutomotiveProcedureSet | None,
    ) -> list[str]:
        """Find procedure IDs that explicitly reference this diagram."""
        if not figure or not figure.identifier or not procedure_set:
            return []

        linked_ids: set[str] = set()
        
        # Check if the figure identifier is in any procedure's referenced_figures
        for procedure in procedure_set.procedures:
            if figure.identifier in procedure.referenced_figures:
                linked_ids.add(procedure.procedure_id)
                
        return sorted(list(linked_ids))
