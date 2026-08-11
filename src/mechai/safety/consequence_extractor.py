"""Extractor for Safety Consequences from text."""

from __future__ import annotations

import re
import uuid

from mechai.contracts.provenance import SourceRef
from mechai.contracts.safety import SafetyConsequence
from mechai.safety.config import SafetyEngineConfig


class ConsequenceExtractor:
    """Extracts safety consequences from text based on linguistic markers."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the consequence extractor."""
        self._config = config or SafetyEngineConfig()

    def extract_consequences(self, text: str, provenance: SourceRef) -> list[SafetyConsequence]:
        """Extract consequences from the text."""
        consequences = []
        
        # Split by sentences or clauses
        clauses = re.split(r'[.;]', text)
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
                
            for pattern in self._config.consequence_patterns:
                match = pattern.search(clause)
                if match:
                    # Clean up the match
                    consequence_text = match.group(0).strip()
                    consequences.append(
                        SafetyConsequence(
                            consequence_id=f"cons_{uuid.uuid4().hex[:8]}",
                            text=consequence_text,
                            confidence=0.9,
                            provenance=provenance,
                        )
                    )
                    break  # Move to next clause
                    
        return consequences
