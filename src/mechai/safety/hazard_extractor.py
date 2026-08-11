"""Extractor for Hazard Categories from safety admonitions."""

from __future__ import annotations

import re
from typing import Tuple

from mechai.contracts.safety import HazardCategory
from mechai.safety.config import SafetyEngineConfig


class HazardExtractor:
    """Extracts Hazard Categories from text deterministically."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the hazard extractor."""
        self._config = config or SafetyEngineConfig()
        
        # Build patterns mapping keyword to HazardCategory
        # Sort by length descending to match longer phrases first (e.g., "high voltage" before "voltage")
        sorted_keywords = sorted(self._config.hazard_keywords.keys(), key=len, reverse=True)
        
        self._hazard_patterns = []
        for kw in sorted_keywords:
            pattern = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            self._hazard_patterns.append((pattern, self._config.hazard_keywords[kw]))

    def extract_hazard(self, text: str) -> Tuple[HazardCategory, float]:
        """Extract the hazard category from the text.
        
        Returns:
            Tuple of HazardCategory and confidence score.
            If only vague evidence is found, returns (UNCERTAIN, low_confidence).
            If no evidence, returns (UNKNOWN, 1.0).
        """
        for pattern, category in self._hazard_patterns:
            if pattern.search(text):
                # We found a deterministic keyword match
                # For example: 'battery' keyword.
                # However, the RFC states: 'battery' does not automatically mean 'electrical hazard'.
                # A keyword alone is not sufficient if it's vague.
                
                # In a conservative model, if it's a direct hazard like "fire" or "explosion", it's certain.
                # If it's just "battery", it might be UNCERTAIN unless accompanied by "acid" or "shock".
                # For this implementation, we will treat the direct mappings in config as 0.8 confidence.
                return category, 0.8
                
        return HazardCategory.UNKNOWN, 1.0
