"""Extractor for Safety Actions and Requirements from text."""

from __future__ import annotations

import re
import uuid
from typing import Tuple

from mechai.contracts.provenance import SourceRef
from mechai.contracts.safety import SafetyAction, SafetyRequirement
from mechai.safety.config import SafetyEngineConfig


class ActionExtractor:
    """Extracts safety actions and requirements from text."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the action extractor."""
        self._config = config or SafetyEngineConfig()

    def extract_actions(self, text: str, provenance: SourceRef) -> list[SafetyAction]:
        """Extract actions from the text."""
        actions = []
        
        clauses = re.split(r'[.;]', text)
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
                
            for pattern in self._config.action_patterns:
                match = pattern.search(clause)
                if match:
                    action_text = match.group(0).strip()
                    is_restriction = "never" in action_text.lower() or "do not" in action_text.lower() or "avoid" in action_text.lower()
                    actions.append(
                        SafetyAction(
                            action_id=f"act_{uuid.uuid4().hex[:8]}",
                            text=action_text,
                            is_restriction=is_restriction,
                            confidence=0.9,
                            provenance=provenance,
                        )
                    )
                    break
                    
        return actions

    def extract_requirements(self, text: str, provenance: SourceRef) -> list[SafetyRequirement]:
        """Extract safety PPE requirements from text."""
        requirements = []
        text_lower = text.lower()
        
        for ppe in self._config.ppe_keywords:
            if ppe in text_lower:
                requirements.append(
                    SafetyRequirement(
                        requirement_id=f"req_{uuid.uuid4().hex[:8]}",
                        equipment=ppe.title(),
                        confidence=0.9,
                        provenance=provenance,
                    )
                )
                
        return requirements
