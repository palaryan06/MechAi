"""Binder for associating safety admonitions with tables."""

from __future__ import annotations

import re
import uuid

from mechai.contracts.provenance import SourceRef
from mechai.contracts.safety import (
    SafetyAdmonition,
    SafetyRelationship,
    SafetyRelationshipType,
)
from mechai.contracts.tables import AutomotiveTableSet
from mechai.safety.config import SafetyEngineConfig


class TableBinder:
    """Binds safety admonitions to tables."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the table binder."""
        self._config = config or SafetyEngineConfig()
        self._table_ref_pattern = re.compile(r"Table\s*([A-Z0-9\-]+)", re.IGNORECASE)

    def bind(
        self, admonition: SafetyAdmonition, table_set: AutomotiveTableSet
    ) -> list[SafetyRelationship]:
        """Find relationships between the admonition and tables."""
        relationships = []
        
        # 1. Textual reference binding
        for match in self._table_ref_pattern.finditer(admonition.raw_text):
            table_ident = f"TABLE {match.group(1).upper()}"
            
            for table in table_set.tables:
                if table.title and table_ident in table.title.upper():
                    relationships.append(
                        SafetyRelationship(
                            relationship_id=f"srel_{uuid.uuid4().hex[:8]}",
                            relationship_type=SafetyRelationshipType.ADMONITION_REFERENCES_TABLE,
                            admonition_id=admonition.admonition_id,
                            target_id=table.table_id,
                            confidence=1.0,
                            evidence=f"Explicit textual reference to {table_ident}",
                            provenance=SourceRef(page_number=admonition.page_span[0]),
                        )
                    )
                    
        return relationships
