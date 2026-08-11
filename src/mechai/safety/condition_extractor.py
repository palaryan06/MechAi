"""Extractor for Safety Conditions from text."""

from __future__ import annotations

import re
import uuid

from mechai.contracts.provenance import SourceRef
from mechai.contracts.safety import SafetyCondition
from mechai.safety.config import SafetyEngineConfig


class ConditionExtractor:
    """Extracts safety conditions from text based on linguistic markers."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the condition extractor."""
        self._config = config or SafetyEngineConfig()

    def extract_conditions(self, text: str, provenance: SourceRef) -> list[SafetyCondition]:
        """Extract conditions from the text."""
        conditions = []
        
        # Split by sentences or clauses
        clauses = re.split(r'[.;]', text)
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
                
            for pattern in self._config.condition_patterns:
                match = pattern.search(clause)
                if match:
                    # Clean up the match
                    condition_text = match.group(0).strip()
                    conditions.append(
                        SafetyCondition(
                            condition_id=f"cond_{uuid.uuid4().hex[:8]}",
                            text=condition_text,
                            confidence=0.9,
                            provenance=provenance,
                        )
                    )
                    break  # Move to next clause
                    
        return conditions
