"""Binder for associating safety admonitions with procedures and steps."""

from __future__ import annotations

import uuid

from mechai.contracts.procedures import AutomotiveProcedureSet
from mechai.contracts.provenance import SourceRef
from mechai.contracts.safety import (
    SafetyAdmonition,
    SafetyRelationship,
    SafetyRelationshipType,
)
from mechai.safety.config import SafetyEngineConfig


class ProcedureBinder:
    """Binds safety admonitions to procedures and steps."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the procedure binder."""
        self._config = config or SafetyEngineConfig()

    def bind(
        self, admonition: SafetyAdmonition, procedure_set: AutomotiveProcedureSet
    ) -> list[SafetyRelationship]:
        """Find relationships between the admonition and procedures."""
        relationships = []
        
        # Determine the page of the admonition
        adm_page = admonition.page_span[0]
        
        for proc in procedure_set.procedures:
            # Only consider procedures on the same page or explicitly referenced
            if proc.page_span[0] <= adm_page <= proc.page_span[1]:
                
                # Check spatial distance (if admonition is directly above procedure)
                vertical_distance = proc.bbox.top - admonition.bbox.bottom
                if 0 <= vertical_distance <= self._config.procedure_binding_distance_pt:
                    relationships.append(
                        SafetyRelationship(
                            relationship_id=f"srel_{uuid.uuid4().hex[:8]}",
                            relationship_type=SafetyRelationshipType.ADMONITION_APPLIES_TO_PROCEDURE,
                            admonition_id=admonition.admonition_id,
                            target_id=proc.procedure_id,
                            confidence=0.8,
                            evidence="Spatial proximity above procedure heading",
                            provenance=SourceRef(page_number=adm_page),
                        )
                    )
                    
                # Check steps
                for step in proc.steps:
                    if step.bbox.top is not None:
                        step_dist = step.bbox.top - admonition.bbox.bottom
                        if 0 <= step_dist <= self._config.procedure_binding_distance_pt:
                            relationships.append(
                                SafetyRelationship(
                                    relationship_id=f"srel_{uuid.uuid4().hex[:8]}",
                                    relationship_type=SafetyRelationshipType.ADMONITION_APPLIES_TO_STEP,
                                    admonition_id=admonition.admonition_id,
                                    target_id=step.step_id,
                                    confidence=0.9,
                                    evidence="Spatial proximity above procedure step",
                                    provenance=SourceRef(page_number=adm_page),
                                )
                            )
                            
        return relationships
