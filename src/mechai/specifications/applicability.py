"""Applicability resolution for facts."""

from __future__ import annotations

import re
from dataclasses import replace

from mechai.contracts.specifications import ApplicabilityContext


class ApplicabilityResolver:
    """Resolves applicability constraints from context."""

    def merge_contexts(self, base: ApplicabilityContext, override: ApplicabilityContext) -> ApplicabilityContext:
        """Merge two applicability contexts. The override takes precedence if set."""
        updates: dict[str, str] = {}
        
        for field_name in override.model_fields:
            override_val = getattr(override, field_name)
            if override_val is not None:
                updates[field_name] = override_val
                
        # If no updates, just return the base
        if not updates:
            return base
            
        return base.model_copy(update=updates)

    def extract_from_text(self, text: str) -> ApplicabilityContext:
        """Extract explicit applicability constraints from a text string.
        
        Examples: 'For K10B', 'A/T only', 'M/T'.
        """
        updates: dict[str, str] = {}
        lower_text = text.lower()
        
        # transmission heuristics
        if "a/t" in lower_text or "automatic" in lower_text:
            updates["transmission"] = "A/T"
        elif "m/t" in lower_text or "manual" in lower_text:
            updates["transmission"] = "M/T"
            
        # Very simple engine code heuristics for MVP (F8D, K10B)
        if "f8d" in lower_text:
            updates["engine_code"] = "F8D"
        elif "k10b" in lower_text:
            updates["engine_code"] = "K10B"
            
        # A/C heuristics
        if "with a/c" in lower_text:
            updates["variant"] = "with A/C"
        elif "without a/c" in lower_text:
            updates["variant"] = "without A/C"
            
        return ApplicabilityContext(**updates)
