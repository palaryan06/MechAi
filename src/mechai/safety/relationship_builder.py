"""Builder for coordinating relationship extraction across binders."""

from __future__ import annotations

from mechai.contracts.diagrams import AutomotiveDiagramSet
from mechai.contracts.procedures import AutomotiveProcedureSet
from mechai.contracts.safety import (
    SafetyAdmonition,
    SafetyRelationship,
)
from mechai.contracts.tables import AutomotiveTableSet
from mechai.safety.config import SafetyEngineConfig
from mechai.safety.diagram_binder import DiagramBinder
from mechai.safety.procedure_binder import ProcedureBinder
from mechai.safety.table_binder import TableBinder


class RelationshipBuilder:
    """Coordinates bindings across all support structures."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize relationship builder."""
        self._config = config or SafetyEngineConfig()
        self._proc_binder = ProcedureBinder(self._config)
        self._diag_binder = DiagramBinder(self._config)
        self._table_binder = TableBinder(self._config)

    def build_relationships(
        self,
        admonitions: list[SafetyAdmonition],
        procedure_set: AutomotiveProcedureSet | None,
        table_set: AutomotiveTableSet | None,
        diagram_set: AutomotiveDiagramSet | None,
    ) -> list[SafetyRelationship]:
        """Build relationships for all admonitions."""
        relationships = []
        
        for admonition in admonitions:
            if procedure_set:
                relationships.extend(self._proc_binder.bind(admonition, procedure_set))
            if table_set:
                relationships.extend(self._table_binder.bind(admonition, table_set))
            if diagram_set:
                relationships.extend(self._diag_binder.bind(admonition, diagram_set))
                
        return relationships
