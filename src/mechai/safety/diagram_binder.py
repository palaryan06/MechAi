"""Binder for associating safety admonitions with diagrams."""

from __future__ import annotations

import re
import uuid

from mechai.contracts.diagrams import AutomotiveDiagramSet
from mechai.contracts.provenance import SourceRef
from mechai.contracts.safety import (
    SafetyAdmonition,
    SafetyRelationship,
    SafetyRelationshipType,
)
from mechai.safety.config import SafetyEngineConfig


class DiagramBinder:
    """Binds safety admonitions to diagrams."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the diagram binder."""
        self._config = config or SafetyEngineConfig()
        self._fig_ref_pattern = re.compile(r"Fig\.\s*([A-Z0-9\-]+)", re.IGNORECASE)

    def bind(
        self, admonition: SafetyAdmonition, diagram_set: AutomotiveDiagramSet
    ) -> list[SafetyRelationship]:
        """Find relationships between the admonition and diagrams."""
        relationships = []
        
        # 1. Textual reference binding
        for match in self._fig_ref_pattern.finditer(admonition.raw_text):
            fig_ident = f"Fig. {match.group(1).upper()}"
            
            for diagram in diagram_set.diagrams:
                if diagram.figure and diagram.figure.identifier and fig_ident in diagram.figure.identifier.upper():
                    relationships.append(
                        SafetyRelationship(
                            relationship_id=f"srel_{uuid.uuid4().hex[:8]}",
                            relationship_type=SafetyRelationshipType.ADMONITION_REFERENCES_DIAGRAM,
                            admonition_id=admonition.admonition_id,
                            target_id=diagram.diagram_id,
                            confidence=1.0,
                            evidence=f"Explicit textual reference to {fig_ident}",
                            provenance=SourceRef(page_number=admonition.page_span[0]),
                        )
                    )
                    
        return relationships
