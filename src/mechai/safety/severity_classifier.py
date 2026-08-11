"""Classifier for safety admonition severity."""

from __future__ import annotations

import re
from typing import Tuple

from mechai.contracts.safety import SafetySeverity
from mechai.safety.config import SafetyEngineConfig


class SeverityClassifier:
    """Classifies the severity of a safety admonition."""

    def __init__(self, config: SafetyEngineConfig | None = None) -> None:
        """Initialize the severity classifier."""
        self._config = config or SafetyEngineConfig()
        
        # Build regex to match leading keywords (e.g., "WARNING:", "CAUTION")
        keywords = "|".join(re.escape(k) for k in self._config.severity_map.keys())
        self._severity_pattern = re.compile(rf"^\s*(?P<label>{keywords})[\s:]*", re.IGNORECASE)

    def classify_severity(self, text: str) -> Tuple[SafetySeverity, str]:
        """Classify the severity based on the text.
        
        Returns:
            Tuple containing the classified SafetySeverity and the original label string.
        """
        match = self._severity_pattern.match(text)
        if match:
            label = match.group("label").upper()
            severity = self._config.severity_map.get(label, SafetySeverity.UNKNOWN_ADMONITION)
            return severity, match.group("label")
            
        return SafetySeverity.UNKNOWN_ADMONITION, "UNKNOWN"
