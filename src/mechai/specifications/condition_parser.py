"""Parser for detecting applicability and measurement conditions from text."""

from __future__ import annotations

from typing import Optional

from mechai.domain.enums import FastenerCondition
from mechai.specifications.config import SpecificationConfig


class ConditionParser:
    """Detects and extracts conditional strings from specification text."""

    def __init__(self, config: SpecificationConfig | None = None) -> None:
        """Initialize the ConditionParser."""
        self._config = config or SpecificationConfig()

    def extract_operating_condition(self, text: str) -> str | None:
        """Extract generic operating conditions like 'when cold', 'engine running'."""
        lower_text = text.lower()
        for kw in self._config.condition_keywords:
            if kw in lower_text:
                return kw
        return None

    def extract_fastener_condition(self, text: str) -> FastenerCondition:
        """Extract fastener preparation state (dry, oil lubricated, threadlocker)."""
        lower_text = text.lower()
        
        for kw in self._config.threadlocker_keywords:
            if kw in lower_text:
                if "blue" in lower_text:
                    return FastenerCondition.THREADLOCKER_BLUE
                if "red" in lower_text:
                    return FastenerCondition.THREADLOCKER_RED
                return FastenerCondition.THREADLOCKER_BLUE  # Default to blue if unspecified
                
        for kw in self._config.lubrication_keywords:
            if kw in lower_text:
                return FastenerCondition.OIL_LUBRICATED
                
        if "anti-seize" in lower_text or "anti seize" in lower_text:
            return FastenerCondition.ANTI_SEIZE
            
        if "sealant" in lower_text:
            return FastenerCondition.SEALANT

        return FastenerCondition.DRY
